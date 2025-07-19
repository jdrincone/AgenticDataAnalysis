"""
PDF Export component for chat conversations.
"""
import streamlit as st
from typing import List, Dict, Any
from pathlib import Path
import tempfile
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import plotly.io as pio
from src.config.settings import config
from src.models.data_models import ChatMessage
from src.core.agents.python_agent import PythonAnalysisAgent

class PDFExporter:
    """Professional PDF exporter for chat conversations."""
    
    def __init__(self):
        self.colors = {
            'primary': colors.HexColor(config.PRIMARY_COLOR),
            'secondary': colors.HexColor(config.SECONDARY_COLOR),
            'light_gray': colors.HexColor('#F5F6F8'),
            'dark_gray': colors.HexColor('#666666'),
            'white': colors.white,
            'black': colors.black
        }
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()
        
        # Header style
        styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subheader style
        styles.add(ParagraphStyle(
            name='CustomSubheader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=self.colors['secondary'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # User message style
        styles.add(ParagraphStyle(
            name='CustomUserMessage',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=20,
            rightIndent=20,
            textColor=self.colors['black'],
            fontName='Helvetica',
            backColor=self.colors['light_gray']
        ))
        
        # Assistant message style
        styles.add(ParagraphStyle(
            name='CustomAssistantMessage',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=20,
            rightIndent=20,
            textColor=self.colors['black'],
            fontName='Helvetica',
            backColor=self.colors['white']
        ))
        
        # Timestamp style
        styles.add(ParagraphStyle(
            name='CustomTimestamp',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=5,
            textColor=self.colors['dark_gray'],
            fontName='Helvetica-Oblique',
            alignment=TA_RIGHT
        ))
        
        # Code style
        styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=30,
            rightIndent=30,
            textColor=self.colors['black'],
            fontName='Courier',
            backColor=colors.HexColor('#F8F9FA')
        ))
        
        return styles
    
    def _create_header(self, story: List, title: str = "Okuo IA DataLab"):
        """Create the PDF header."""
        # Logo/Title
        story.append(Paragraph(f"🤖 {title}", self.styles['CustomHeader']))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("Laboratorio de Análisis Inteligente de Datos", self.styles['CustomSubheader']))
        story.append(Spacer(1, 30))
        
        # Export info
        export_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"Reporte generado el: {export_time}", self.styles['CustomTimestamp']))
        story.append(Spacer(1, 20))
    
    def _add_executive_summary(self, story: List, agent: PythonAnalysisAgent):
        """Add executive summary with key insights and visualizations."""
        chat_history = agent.get_chat_history()
        
        if not chat_history:
            return
        
        # Extract user questions and AI responses with visualizations
        qa_pairs = []
        current_user_question = None
        current_ai_response = None
        current_images = []
        
        for msg_index, msg in enumerate(chat_history):
            if msg.sender == "user":
                # If we have a previous Q&A pair, save it
                if current_user_question and current_ai_response:
                    qa_pairs.append({
                        'question': current_user_question,
                        'response': current_ai_response,
                        'images': current_images
                    })
                
                # Start new Q&A pair
                current_user_question = msg.content
                current_ai_response = None
                current_images = []
                
            elif msg.sender == "assistant":
                current_ai_response = msg.content
                # Get images for this response
                current_images = agent.get_output_images(msg_index)
        
        # Add the last Q&A pair
        if current_user_question and current_ai_response:
            qa_pairs.append({
                'question': current_user_question,
                'response': current_ai_response,
                'images': current_images
            })
        
        # Add executive summary section
        story.append(Paragraph("📊 <b>Resumen Ejecutivo - Análisis de Datos</b>", self.styles['CustomHeader']))
        story.append(Spacer(1, 20))
        
        # Add each Q&A pair
        for i, qa_pair in enumerate(qa_pairs):
            # Question
            story.append(Paragraph(f"<b>Pregunta {i+1}:</b> {qa_pair['question']}", self.styles['CustomSubheader']))
            story.append(Spacer(1, 10))
            
            # Response (summarized)
            summary = self._extract_key_insights(qa_pair['response'])
            story.append(Paragraph(f"<b>Respuesta:</b> {summary}", self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Add visualizations
            for image_path in qa_pair['images']:
                try:
                    fig = agent.load_plotly_figure(image_path)
                    if fig:
                        # Save plotly figure as image
                        img_temp_path = self._save_plotly_figure(fig, image_path)
                        if img_temp_path and os.path.exists(img_temp_path):
                            # Add image to PDF
                            img = Image(img_temp_path, width=6*inch, height=4*inch)
                            img.hAlign = 'CENTER'
                            story.append(Spacer(1, 10))
                            story.append(img)
                            story.append(Spacer(1, 10))
                            
                            # Store temp path for cleanup later
                            if not hasattr(self, 'temp_files'):
                                self.temp_files = []
                            self.temp_files.append(img_temp_path)
                        else:
                            st.warning(f"No se pudo crear la imagen temporal para {image_path}")
                    else:
                        st.warning(f"No se pudo cargar la figura de plotly para {image_path}")
                except Exception as e:
                    st.warning(f"No se pudo incluir la imagen {image_path}: {str(e)}")
                    print(f"Debug - Error details for {image_path}: {e}")
            
            story.append(Spacer(1, 20))
    
    def _extract_key_insights(self, response: str) -> str:
        """Extract key insights from AI response for executive summary."""
        # Simple extraction of key points
        lines = response.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Look for lines that contain key insights
            if any(keyword in line.lower() for keyword in [
                'encontramos', 'descubrimos', 'observamos', 'vemos que', 
                'conclusión', 'resultado', 'tendencia', 'patrón',
                'mayor', 'menor', 'promedio', 'total', 'porcentaje',
                'gráfico', 'visualización', 'análisis'
            ]):
                if len(line) > 20:  # Only meaningful lines
                    key_points.append(line)
        
        # If no key points found, take first few sentences
        if not key_points:
            sentences = response.split('.')
            key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        # Limit to 3 key points
        key_points = key_points[:3]
        
        return '. '.join(key_points) + '.' if key_points else response[:200] + "..."
    
    def _save_plotly_figure(self, fig, filename: str) -> str:
        """Save plotly figure as temporary image file."""
        try:
            # Create temp directory in project using config paths
            temp_dir = config.BASE_DIR / "temp_pdf_images"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            import uuid
            unique_id = str(uuid.uuid4())
            temp_path = temp_dir / f"plotly_{unique_id}.png"
            
            # Save as PNG with high quality
            fig.write_image(str(temp_path), format='png', width=800, height=600, scale=2)
            
            # Verify the file was created
            if not temp_path.exists():
                raise FileNotFoundError(f"Failed to create image file: {temp_path}")
            
            return str(temp_path)
        except Exception as e:
            st.error(f"Error saving plotly figure: {str(e)}")
            print(f"Debug - Current working directory: {os.getcwd()}")
            print(f"Debug - Temp directory path: {config.BASE_DIR / 'temp_pdf_images'}")
            print(f"Debug - Temp directory exists: {(config.BASE_DIR / 'temp_pdf_images').exists()}")
            print(f"Debug - Config BASE_DIR: {config.BASE_DIR}")
            print(f"Debug - Config BASE_DIR exists: {config.BASE_DIR.exists()}")
            return None
    
    def _add_intermediate_outputs(self, story: List, agent: PythonAnalysisAgent):
        """Add intermediate outputs section."""
        intermediate_outputs = agent.get_intermediate_outputs()
        
        if intermediate_outputs:
            story.append(Paragraph("🔍 <b>Proceso de Análisis</b>", self.styles['CustomSubheader']))
            story.append(Spacer(1, 15))
            
            for i, output in enumerate(intermediate_outputs):
                story.append(Paragraph(f"<b>Paso {i+1}:</b>", self.styles['Normal']))
                
                if 'thought' in output:
                    story.append(Paragraph(f"<b>Razonamiento:</b> {output['thought']}", self.styles['Normal']))
                
                if 'code' in output:
                    story.append(Paragraph("<b>Código:</b>", self.styles['Normal']))
                    story.append(Paragraph(output['code'], self.styles['CodeBlock']))
                
                if 'output' in output:
                    story.append(Paragraph(f"<b>Salida:</b> {output['output']}", self.styles['Normal']))
                
                story.append(Spacer(1, 10))
    
    def export_chat_to_pdf(self, agent: PythonAnalysisAgent, filename: str = None) -> str:
        """Export chat conversation to PDF."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_export_{timestamp}.pdf"
        
        # Initialize temp files list
        self.temp_files = []
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Add header
            self._create_header(story)
            
            # Add executive summary instead of full conversation
            self._add_executive_summary(story, agent)
            
            # Build PDF
            doc.build(story)
        
        except Exception as e:
            print(f"Error during PDF generation: {e}")
            raise e
        finally:
            # Clean up temp files after PDF is built
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Could not remove temp file {temp_file}: {e}")
            
            # Clean up temp directory
            temp_dir = config.BASE_DIR / "temp_pdf_images"
            if temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Could not remove temp directory {temp_dir}: {e}")
        
        return filename

def render_pdf_export_button(agent: PythonAnalysisAgent):
    """Render PDF export button in the UI."""
    st.subheader("📄 Exportar Conversación")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("📊 Exportar a PDF", type="primary", use_container_width=True):
            try:
                # Create exporter
                exporter = PDFExporter()
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Okuo_DataLab_Resumen_Ejecutivo_{timestamp}.pdf"
                
                # Export to PDF
                pdf_path = exporter.export_chat_to_pdf(agent, filename)
                
                # Read the PDF file
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Create download button
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success(f"✅ Reporte PDF generado exitosamente: {filename}")
                
                # Clean up temporary file
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")
    
    with col2:
        st.info("""
        **📋 Información del Reporte Ejecutivo:**
        - Preguntas principales y respuestas clave
        - Visualizaciones explicativas
        - Insights y conclusiones importantes
        - Formato profesional para presentación
        - Resumen gerencial conciso
        """) 