"""
Storytelling Agent for generating professional PDF reports with insights.
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import os
from datetime import datetime
import json
import re
from dataclasses import dataclass

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pickle

from src.config.settings import config
from src.models.data_models import ChatMessage, AnalysisResult
from src.core.agents.python_agent import PythonAnalysisAgent


@dataclass
class ConversationInsight:
    """Represents a key insight extracted from conversation."""
    question: str
    answer: str
    key_findings: List[str]
    data_insights: List[str]
    recommendations: List[str]
    visualizations: List[str]
    confidence_score: float


class StorytellingAgent:
    """
    Professional storytelling agent that analyzes conversations and generates
    comprehensive PDF reports with insights and visualizations.
    """
    
    def __init__(self):
        self.colors = {
            'primary': colors.HexColor(config.PRIMARY_COLOR),
            'secondary': colors.HexColor(config.SECONDARY_COLOR),
            'accent': colors.HexColor(config.ACCENT_COLOR),
            'light_gray': colors.HexColor('#F5F6F8'),
            'dark_gray': colors.HexColor('#666666'),
            'white': colors.white,
            'black': colors.black
        }
        self.styles = self._create_professional_styles()
        self.temp_files = []
        self.prompt = self._load_storytelling_prompt()
    
    def _load_storytelling_prompt(self) -> str:
        """Load the storytelling prompt from the prompts directory."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "storytelling_prompt.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            st.error(f"Storytelling prompt not found at {prompt_path}")
            return ""
    
    def _create_professional_styles(self):
        """Create professional paragraph styles for the report."""
        styles = getSampleStyleSheet()
        
        # Main title style
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceBefore=20
        ))
        
        # Section title style
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=25,
            textColor=self.colors['secondary'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leftIndent=10
        ))
        
        # Subsection title style
        styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=self.colors['accent'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leftIndent=15
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=self.colors['black'],
            fontName='Helvetica',
            leftIndent=20,
            rightIndent=20
        ))
        
        # Insight box style
        styles.add(ParagraphStyle(
            name='InsightBox',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=25,
            rightIndent=25,
            textColor=self.colors['black'],
            fontName='Helvetica',
            backColor=self.colors['light_gray'],
            borderWidth=1,
            borderColor=self.colors['primary'],
            borderPadding=10
        ))
        
        # Question style
        styles.add(ParagraphStyle(
            name='Question',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            leftIndent=20,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        # Answer style
        styles.add(ParagraphStyle(
            name='Answer',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=5,
            leftIndent=30,
            rightIndent=20,
            textColor=self.colors['black'],
            fontName='Helvetica'
        ))
        
        # Recommendation style
        styles.add(ParagraphStyle(
            name='Recommendation',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=25,
            rightIndent=25,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold',
            backColor=self.colors['light_gray'],
            borderWidth=1,
            borderColor=self.colors['secondary'],
            borderPadding=8
        ))
        
        return styles
    
    def analyze_conversation(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult]) -> List[ConversationInsight]:
        """
        Analyze the conversation using the storytelling prompt to extract key insights.
        """
        insights = []
        
        # Group messages by conversation turns
        conversation_turns = self._group_conversation_turns(chat_history, analysis_results)
        
        # Use the storytelling prompt to guide the analysis
        for turn in conversation_turns:
            # Apply storytelling prompt methodology
            insight = self._apply_storytelling_analysis(turn)
            insights.append(insight)
        
        return insights
    
    def _apply_storytelling_analysis(self, turn: Dict) -> ConversationInsight:
        """
        Apply the storytelling prompt methodology to analyze a conversation turn.
        """
        question = turn['question']
        answer = turn['answer']
        
        # Extract insights following the prompt guidelines
        key_findings = self._extract_key_findings_with_prompt(answer)
        data_insights = self._extract_data_insights_with_prompt(answer)
        recommendations = self._generate_recommendations_with_prompt(question, answer)
        
        return ConversationInsight(
            question=question,
            answer=answer,
            key_findings=key_findings,
            data_insights=data_insights,
            recommendations=recommendations,
            visualizations=turn['visualizations'],
            confidence_score=self._calculate_confidence(answer)
        )
    
    def _extract_key_findings_with_prompt(self, answer: str) -> List[str]:
        """
        Extract key findings following the storytelling prompt guidelines.
        Focus on insights that impact business decisions.
        """
        findings = []
        
        # Look for statistical findings
        stat_patterns = [
            r'media.*?(\d+\.?\d*)',
            r'promedio.*?(\d+\.?\d*)',
            r'correlación.*?(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*toneladas',
            r'(\d+\.?\d*)\s*kWh'
        ]
        
        for pattern in stat_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                findings.append(f"Valor estadístico encontrado: {match}")
        
        # Look for patterns and trends
        pattern_keywords = ['patrón', 'tendencia', 'correlación', 'relación', 'distribución']
        for keyword in pattern_keywords:
            if keyword in answer.lower():
                # Extract the sentence containing the keyword
                sentences = answer.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        findings.append(f"Patrón detectado: {sentence.strip()}")
                        break
        
        # Look for anomalies
        anomaly_keywords = ['anomalía', 'valor atípico', 'outlier', 'inusual', 'extraordinario']
        for keyword in anomaly_keywords:
            if keyword in answer.lower():
                sentences = answer.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        findings.append(f"Anomalía identificada: {sentence.strip()}")
                        break
        
        return findings[:5]  # Limit to top 5 findings
    
    def _extract_data_insights_with_prompt(self, answer: str) -> List[str]:
        """
        Extract data insights following the storytelling prompt guidelines.
        Focus on business implications and actionable insights.
        """
        insights = []
        
        # Look for business insights
        business_keywords = [
            'eficiencia', 'productividad', 'optimización', 'mejora', 'oportunidad',
            'riesgo', 'problema', 'ventaja', 'desventaja', 'impacto'
        ]
        
        for keyword in business_keywords:
            if keyword in answer.lower():
                sentences = answer.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        insights.append(f"Insight de negocio: {sentence.strip()}")
                        break
        
        # Look for recommendations
        recommendation_keywords = ['recomiendo', 'sugiero', 'debería', 'conviene', 'es importante']
        for keyword in recommendation_keywords:
            if keyword in answer.lower():
                sentences = answer.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        insights.append(f"Recomendación: {sentence.strip()}")
                        break
        
        return insights[:3]  # Limit to top 3 insights
    
    def _generate_recommendations_with_prompt(self, question: str, answer: str) -> List[str]:
        """
        Generate recommendations following the storytelling prompt guidelines.
        Focus on specific, measurable, and actionable recommendations.
        """
        recommendations = []
        
        # Extract recommendations from the answer
        rec_patterns = [
            r'recomiendo.*?\.',
            r'sugiero.*?\.',
            r'debería.*?\.',
            r'conviene.*?\.',
            r'es importante.*?\.'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE | re.DOTALL)
            for match in matches:
                recommendations.append(match.strip())
        
        # Generate additional recommendations based on the analysis
        if 'correlación' in answer.lower() or 'relación' in answer.lower():
            recommendations.append("Monitorear continuamente las variables correlacionadas para detectar cambios en la relación.")
        
        if 'anomalía' in answer.lower() or 'valor atípico' in answer.lower():
            recommendations.append("Investigar las causas de las anomalías identificadas para prevenir problemas futuros.")
        
        if 'eficiencia' in answer.lower() or 'productividad' in answer.lower():
            recommendations.append("Implementar mejoras en los procesos identificados como ineficientes.")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _group_conversation_turns(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult]) -> List[Dict]:
        """Group messages into conversation turns."""
        turns = []
        current_question = None
        current_answer = None
        current_visualizations = []
        
        for i, msg in enumerate(chat_history):
            if msg.role == "user":
                # Save previous turn if exists
                if current_question and current_answer:
                    turns.append({
                        'question': current_question,
                        'answer': current_answer,
                        'visualizations': current_visualizations
                    })
                
                # Start new turn
                current_question = msg.content
                current_answer = None
                current_visualizations = []
                
            elif msg.role == "assistant":
                current_answer = msg.content
                # Get visualizations for this turn
                if i < len(analysis_results):
                    result = analysis_results[i]
                    if hasattr(result, 'output_image_paths'):
                        current_visualizations = result.output_image_paths
        
        # Add last turn
        if current_question and current_answer:
            turns.append({
                'question': current_question,
                'answer': current_answer,
                'visualizations': current_visualizations
            })
        
        return turns
    
    def _extract_key_findings(self, answer: str) -> List[str]:
        """Extract key findings from the answer."""
        findings = []
        
        # Look for patterns that indicate findings
        patterns = [
            r'encontramos que\s+(.+)',
            r'descubrimos que\s+(.+)',
            r'observamos que\s+(.+)',
            r'vemos que\s+(.+)',
            r'la conclusión es\s+(.+)',
            r'el resultado muestra\s+(.+)',
            r'se puede observar\s+(.+)',
            r'se evidencia\s+(.+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 20:
                    findings.append(match.strip())
        
        # If no patterns found, extract sentences with key words
        if not findings:
            sentences = answer.split('.')
            key_words = ['encontró', 'descubrió', 'observó', 'evidenció', 'mostró', 'indicó', 'sugiere']
            
            for sentence in sentences:
                if any(word in sentence.lower() for word in key_words):
                    if len(sentence.strip()) > 30:
                        findings.append(sentence.strip())
        
        return findings[:5]  # Limit to 5 findings
    
    def _extract_data_insights(self, answer: str) -> List[str]:
        """Extract data-specific insights."""
        insights = []
        
        # Look for numerical patterns
        number_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:por ciento|%)',
            r'(\d+(?:\.\d+)?)\s*(?:toneladas|tons?)',
            r'(\d+(?:\.\d+)?)\s*(?:horas|hrs?)',
            r'(\d+(?:\.\d+)?)\s*(?:kWh)',
            r'promedio de\s+(\d+(?:\.\d+)?)',
            r'media de\s+(\d+(?:\.\d+)?)',
            r'total de\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                # Find the sentence containing this number
                sentences = answer.split('.')
                for sentence in sentences:
                    if match in sentence:
                        if len(sentence.strip()) > 20:
                            insights.append(sentence.strip())
                            break
        
        return insights[:3]  # Limit to 3 insights
    
    def _generate_recommendations(self, question: str, answer: str) -> List[str]:
        """Generate recommendations based on the Q&A."""
        recommendations = []
        
        # Analyze question type and generate appropriate recommendations
        question_lower = question.lower()
        
        if 'análisis' in question_lower or 'exploratorio' in question_lower:
            recommendations.extend([
                "Realizar análisis más profundos de las variables identificadas",
                "Considerar análisis de correlación entre variables clave",
                "Implementar monitoreo continuo de las métricas identificadas"
            ])
        
        if 'rendimiento' in question_lower or 'producción' in question_lower:
            recommendations.extend([
                "Optimizar los procesos de producción basándose en los patrones identificados",
                "Establecer KPIs para monitorear el rendimiento continuamente",
                "Implementar alertas para valores fuera del rango normal"
            ])
        
        if 'calidad' in question_lower or 'durabilidad' in question_lower:
            recommendations.extend([
                "Revisar los parámetros de calidad identificados",
                "Implementar controles de calidad más estrictos",
                "Capacitar al personal en los estándares de calidad"
            ])
        
        if 'tiempo' in question_lower or 'perdido' in question_lower:
            recommendations.extend([
                "Analizar las causas raíz del tiempo perdido",
                "Implementar mejoras en los procesos para reducir paradas",
                "Establecer protocolos de mantenimiento preventivo"
            ])
        
        # Add general recommendations if none specific
        if not recommendations:
            recommendations = [
                "Continuar monitoreando las métricas clave identificadas",
                "Realizar análisis periódicos para detectar tendencias",
                "Compartir los hallazgos con el equipo de operaciones"
            ]
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def _calculate_confidence(self, answer: str) -> float:
        """Calculate confidence score based on answer quality."""
        score = 0.5  # Base score
        
        # Add points for specific indicators
        if 'gráfico' in answer.lower() or 'visualización' in answer.lower():
            score += 0.2
        
        if any(word in answer.lower() for word in ['encontramos', 'descubrimos', 'observamos']):
            score += 0.15
        
        if any(word in answer.lower() for word in ['conclusión', 'resultado', 'análisis']):
            score += 0.1
        
        if len(answer) > 200:  # Detailed answer
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def generate_storytelling_pdf(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult], filename: str = None) -> str:
        """
        Generate a professional storytelling PDF report.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"storytelling_report_{timestamp}.pdf"
        
        # Create temporary file
        temp_dir = Path(tempfile.gettempdir())
        pdf_path = temp_dir / filename
        
        # Analyze conversation
        insights = self.analyze_conversation(chat_history, analysis_results)
        
        # Generate PDF
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Add content sections
        self._add_cover_page(story)
        story.append(PageBreak())
        
        self._add_executive_summary(story, insights)
        story.append(PageBreak())
        
        self._add_conversation_analysis(story, insights)
        
        if any(insight.visualizations for insight in insights):
            story.append(PageBreak())
            self._add_visualizations_section(story, insights)
        
        story.append(PageBreak())
        self._add_recommendations_section(story, insights)
        
        story.append(PageBreak())
        self._add_technical_details(story, chat_history, analysis_results)
        
        # Build PDF
        doc.build(story)
        
        # Cleanup temp files
        self._cleanup_temp_files()
        
        return str(pdf_path)
    
    def _add_cover_page(self, story: List):
        """Add professional cover page."""
        # Title
        story.append(Paragraph("📊 <b>Reporte de Análisis Inteligente</b>", self.styles['MainTitle']))
        story.append(Spacer(1, 40))
        
        # Subtitle
        story.append(Paragraph("Storytelling Profesional de Conversación de Datos", self.styles['SectionTitle']))
        story.append(Spacer(1, 30))
        
        # Company info
        story.append(Paragraph("Okuo IA DataLab", self.styles['SubsectionTitle']))
        story.append(Paragraph("Laboratorio de Análisis Inteligente de Datos", self.styles['CustomBodyText']))
        story.append(Spacer(1, 40))
        
        # Date
        export_time = datetime.now().strftime("%d de %B de %Y")
        story.append(Paragraph(f"Generado el: {export_time}", self.styles['CustomBodyText']))
        story.append(Spacer(1, 60))
        
        # Description
        story.append(Paragraph(
            "Este reporte presenta un análisis profundo de la conversación mantenida con nuestro agente de análisis de datos, "
            "extrayendo insights clave, visualizaciones relevantes y recomendaciones estratégicas basadas en los hallazgos.",
            self.styles['CustomBodyText']
        ))
    
    def _add_executive_summary(self, story: List, insights: List[ConversationInsight]):
        """Add executive summary section."""
        story.append(Paragraph("📋 <b>Resumen Ejecutivo</b>", self.styles['SectionTitle']))
        story.append(Spacer(1, 20))
        
        # Overview
        story.append(Paragraph(
            "Este reporte presenta los hallazgos más importantes extraídos de la conversación de análisis de datos, "
            f"incluyendo {len(insights)} consultas principales que fueron analizadas en profundidad.",
            self.styles['CustomBodyText']
        ))
        story.append(Spacer(1, 15))
        
        # Key insights summary
        all_findings = []
        for insight in insights:
            all_findings.extend(insight.key_findings)
        
        if all_findings:
            story.append(Paragraph("<b>Hallazgos Principales:</b>", self.styles['SubsectionTitle']))
            for i, finding in enumerate(all_findings[:5], 1):
                story.append(Paragraph(f"• {finding}", self.styles['CustomBodyText']))
            story.append(Spacer(1, 15))
        
        # Data insights summary
        all_data_insights = []
        for insight in insights:
            all_data_insights.extend(insight.data_insights)
        
        if all_data_insights:
            story.append(Paragraph("<b>Insights de Datos:</b>", self.styles['SubsectionTitle']))
            for i, data_insight in enumerate(all_data_insights[:3], 1):
                story.append(Paragraph(f"• {data_insight}", self.styles['CustomBodyText']))
    
    def _add_conversation_analysis(self, story: List, insights: List[ConversationInsight]):
        """Add detailed conversation analysis."""
        story.append(Paragraph("💬 <b>Análisis de Conversación</b>", self.styles['SectionTitle']))
        story.append(Spacer(1, 20))
        
        for i, insight in enumerate(insights, 1):
            # Question
            story.append(Paragraph(f"<b>Consulta {i}:</b> {insight.question}", self.styles['Question']))
            
            # Answer summary
            answer_summary = self._summarize_answer(insight.answer)
            story.append(Paragraph(f"<b>Respuesta:</b> {answer_summary}", self.styles['Answer']))
            
            # Key findings
            if insight.key_findings:
                story.append(Paragraph("<b>Hallazgos Clave:</b>", self.styles['SubsectionTitle']))
                for finding in insight.key_findings:
                    story.append(Paragraph(f"• {finding}", self.styles['CustomBodyText']))
            
            # Data insights
            if insight.data_insights:
                story.append(Paragraph("<b>Insights de Datos:</b>", self.styles['SubsectionTitle']))
                for data_insight in insight.data_insights:
                    story.append(Paragraph(f"• {data_insight}", self.styles['CustomBodyText']))
            
            story.append(Spacer(1, 20))
    
    def _add_visualizations_section(self, story: List, insights: List[ConversationInsight]):
        """Add visualizations section."""
        story.append(Paragraph("📈 <b>Visualizaciones y Gráficos</b>", self.styles['SectionTitle']))
        story.append(Spacer(1, 20))
        
        for i, insight in enumerate(insights, 1):
            if insight.visualizations:
                story.append(Paragraph(f"<b>Visualizaciones para Consulta {i}:</b>", self.styles['SubsectionTitle']))
                
                for viz_path in insight.visualizations:
                    try:
                        # Load and save plotly figure
                        img_path = self._process_visualization(viz_path)
                        if img_path:
                            img = Image(img_path, width=6*inch, height=4*inch)
                            img.hAlign = 'CENTER'
                            story.append(Spacer(1, 10))
                            story.append(img)
                            story.append(Spacer(1, 10))
                    except Exception as e:
                        st.error(f"Error processing visualization {viz_path}: {str(e)}")
                
                story.append(Spacer(1, 15))
    
    def _add_recommendations_section(self, story: List, insights: List[ConversationInsight]):
        """Add recommendations section."""
        story.append(Paragraph("🎯 <b>Recomendaciones Estratégicas</b>", self.styles['SectionTitle']))
        story.append(Spacer(1, 20))
        
        # Collect all recommendations
        all_recommendations = []
        for insight in insights:
            all_recommendations.extend(insight.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        # Add recommendations
        for i, recommendation in enumerate(unique_recommendations[:8], 1):
            story.append(Paragraph(f"<b>{i}.</b> {recommendation}", self.styles['Recommendation']))
            story.append(Spacer(1, 8))
    
    def _add_technical_details(self, story: List, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult]):
        """Add technical details section."""
        story.append(Paragraph("🔧 <b>Detalles Técnicos</b>", self.styles['SectionTitle']))
        story.append(Spacer(1, 20))
        
        # Conversation statistics
        story.append(Paragraph("<b>Estadísticas de la Conversación:</b>", self.styles['SubsectionTitle']))
        story.append(Paragraph(f"• Total de mensajes: {len(chat_history)}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"• Consultas del usuario: {len([m for m in chat_history if m.role == 'user'])}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"• Respuestas del agente: {len([m for m in chat_history if m.role == 'assistant'])}", self.styles['CustomBodyText']))
        story.append(Paragraph(f"• Análisis realizados: {len(analysis_results)}", self.styles['CustomBodyText']))
        
        # Total visualizations
        total_viz = sum(len(result.output_image_paths) if hasattr(result, 'output_image_paths') else 0 for result in analysis_results)
        story.append(Paragraph(f"• Visualizaciones generadas: {total_viz}", self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 20))
        
        # Methodology
        story.append(Paragraph("<b>Metodología:</b>", self.styles['SubsectionTitle']))
        story.append(Paragraph(
            "Este reporte fue generado utilizando análisis de lenguaje natural y técnicas de extracción de insights "
            "para identificar patrones, hallazgos clave y recomendaciones basadas en la conversación mantenida con "
            "el agente de análisis de datos de Okuo IA DataLab.",
            self.styles['CustomBodyText']
        ))
    
    def _summarize_answer(self, answer: str) -> str:
        """Summarize the answer for the report."""
        # Take first few sentences that contain key information
        sentences = answer.split('.')
        summary_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(keyword in sentence.lower() for keyword in [
                'encontramos', 'descubrimos', 'observamos', 'vemos', 'conclusión', 'resultado', 'análisis'
            ]):
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 2:
                    break
        
        if not summary_sentences:
            # Take first meaningful sentence
            for sentence in sentences:
                if len(sentence.strip()) > 50:
                    summary_sentences.append(sentence.strip())
                    break
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else answer[:200] + "..."
    
    def _process_visualization(self, viz_path: str) -> Optional[str]:
        """Process visualization and return image path."""
        try:
            figure_path = config.PLOTLY_FIGURES_DIR / viz_path
            
            if figure_path.exists():
                with open(figure_path, "rb") as f:
                    fig = pickle.load(f)
                
                # Save as temporary image
                temp_img_path = self._save_plotly_figure(fig, viz_path)
                if temp_img_path:
                    self.temp_files.append(temp_img_path)
                    return temp_img_path
            
            return None
        except Exception as e:
            st.error(f"Error processing visualization {viz_path}: {str(e)}")
            return None
    
    def _save_plotly_figure(self, fig, filename: str) -> Optional[str]:
        """Save plotly figure as temporary image file."""
        try:
            # Create temporary file
            temp_dir = Path(tempfile.gettempdir())
            img_filename = f"viz_{filename.replace('.pickle', '.png')}"
            img_path = temp_dir / img_filename
            
            # Save figure as PNG
            fig.write_image(str(img_path), width=800, height=600, scale=2)
            
            return str(img_path)
        except Exception as e:
            st.error(f"Error saving figure {filename}: {str(e)}")
            return None
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                st.warning(f"Could not remove temp file {temp_file}: {str(e)}")
        
        self.temp_files = [] 