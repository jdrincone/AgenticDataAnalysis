"""
PDF Export component for chat conversations with professional storytelling.
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
from src.core.agents.storytelling_agent import StorytellingAgent

class PDFExporter:
    """Professional PDF exporter with storytelling capabilities."""
    
    def __init__(self):
        self.storytelling_agent = StorytellingAgent()
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
            backColor=self.colors['light_gray']
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
    
    def _add_executive_summary(self, story: List, chat_history: List[ChatMessage], analysis_results: List):
        """Add executive summary with key insights and visualizations."""
        if not chat_history:
            return
        
        # Extract user questions and AI responses with visualizations
        qa_pairs = []
        current_user_question = None
        current_ai_response = None
        current_images = []
        
        for msg_index, msg in enumerate(chat_history):
            if msg.role == "user":
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
                
            elif msg.role == "assistant":
                current_ai_response = msg.content
                # Get images for this response from analysis results
                if msg_index < len(analysis_results):
                    current_images = analysis_results[msg_index].output_image_paths if hasattr(analysis_results[msg_index], 'output_image_paths') else []
        
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
                    # Load plotly figure from pickle file
                    import pickle
                    figure_path = config.PLOTLY_FIGURES_DIR / image_path
                    
                    if figure_path.exists():
                        with open(figure_path, "rb") as f:
                            fig = pickle.load(f)
                        
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
                            print(f"No se pudo crear la imagen temporal para {image_path}")
                    else:
                        print(f"No se encontró el archivo de figura: {figure_path}")
                except Exception as e:
                    print(f"No se pudo incluir la imagen {image_path}: {str(e)}")
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
            # Create temporary file
            temp_dir = Path(tempfile.gettempdir())
            img_filename = f"pdf_viz_{filename.replace('.pickle', '.png')}"
            img_path = temp_dir / img_filename
            
            # Save figure as PNG
            fig.write_image(str(img_path), width=800, height=600, scale=2)
            
            return str(img_path)
        except Exception as e:
            print(f"Error saving figure {filename}: {str(e)}")
            return None
    
    def _add_intermediate_outputs(self, story: List, agent: PythonAnalysisAgent):
        """Add intermediate outputs section."""
        if hasattr(agent, 'intermediate_outputs') and agent.intermediate_outputs:
            story.append(Paragraph("📝 <b>Salidas Intermedias</b>", self.styles['CustomSubheader']))
            story.append(Spacer(1, 15))
            
            for i, output in enumerate(agent.intermediate_outputs, 1):
                story.append(Paragraph(f"<b>Paso {i}:</b>", self.styles['Normal']))
                story.append(Paragraph(output, self.styles['CodeBlock']))
                story.append(Spacer(1, 10))
    
    def export_chat_to_pdf(self, chat_history: List[ChatMessage], analysis_results: List, filename: str = None) -> str:
        """
        Export chat conversation to PDF using professional storytelling.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"okuo_analysis_report_{timestamp}.pdf"
        
        # Use the storytelling agent to generate professional PDF
        try:
            pdf_path = self.storytelling_agent.generate_storytelling_pdf(
                chat_history=chat_history,
                analysis_results=analysis_results,
                filename=filename
            )
            
            st.success(f"✅ Reporte profesional generado exitosamente: {filename}")
            return pdf_path
            
        except Exception as e:
            st.error(f"❌ Error generando reporte profesional: {str(e)}")
            
            # Fallback to simple PDF if storytelling fails
            st.warning("🔄 Generando reporte simple como respaldo...")
            return self._generate_simple_pdf(chat_history, analysis_results, filename)
    
    def _generate_simple_pdf(self, chat_history: List[ChatMessage], analysis_results: List, filename: str) -> str:
        """Generate simple PDF as fallback."""
        # Create temporary file
        temp_dir = Path(tempfile.gettempdir())
        pdf_path = temp_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Add header
        self._create_header(story)
        
        # Add executive summary
        self._add_executive_summary(story, chat_history, analysis_results)
        
        # Build PDF
        doc.build(story)
        
        return str(pdf_path)


def render_pdf_export_button():
    """Render PDF export button with storytelling option."""
    # Check if this component has already been rendered to prevent duplication
    if 'pdf_export_rendered' in st.session_state:
        return
    
    # Mark as rendered
    st.session_state.pdf_export_rendered = True
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📄 Exportar Reporte")
        
        # Get chat history and analysis results from session state
        if 'app_state' not in st.session_state:
            st.info("💡 Inicia una conversación para generar un reporte")
            return
        
        app_state = st.session_state.app_state
        chat_history = app_state.chat_history
        analysis_results = app_state.analysis_results
        
        if not chat_history:
            st.info("💡 Inicia una conversación para generar un reporte")
            return
        
        # Export button with fixed unique key
        if st.button("🚀 Generar Reporte Profesional", type="primary", use_container_width=True, key="pdf_export_button_unique"):
            with st.spinner("🔄 Generando reporte profesional con storytelling..."):
                try:
                    exporter = PDFExporter()
                    pdf_path = exporter.export_chat_to_pdf(chat_history, analysis_results)
                    
                    if pdf_path and os.path.exists(pdf_path):
                        # Read PDF file
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        # Create download button
                        download_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"okuo_storytelling_report_{download_timestamp}.pdf"
                        
                        st.download_button(
                            label="📥 Descargar Reporte Profesional",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key="pdf_download_button_unique"
                        )
                        
                        st.success("✅ Reporte generado exitosamente con storytelling profesional")
                        
                        # Cleanup
                        try:
                            os.remove(pdf_path)
                        except:
                            pass
                    else:
                        st.error("❌ No se pudo generar el reporte")
                        
                except Exception as e:
                    st.error(f"❌ Error generando reporte: {str(e)}")
                    st.exception(e)
        
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #1C8074;">
        <h4 style="color: #1C8074; margin: 0 0 10px 0;">🎯 Reporte Profesional con Storytelling</h4>
        <p style="margin: 0; color: #666;">
        Este reporte incluye:
        • 📊 Resumen ejecutivo con insights clave<br>
        • 💬 Análisis profundo de la conversación<br>
        • 📈 Visualizaciones y gráficos relevantes<br>
        • 🎯 Recomendaciones estratégicas<br>
        • 🔧 Detalles técnicos del análisis
        </p>
        </div>
        """, unsafe_allow_html=True) 