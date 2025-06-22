import os
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
class Settings(BaseSettings):
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465
    gmail_user: str = ""
    gmail_app_password: str = ""
    recipient_email: str = "hola@efficiency24.io"
    
    class Config:
        env_file = ".env"

settings = Settings(
    gmail_user=os.getenv("GMAIL_USER", ""),
    gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
    recipient_email=os.getenv("RECIPIENT_EMAIL", "hola@efficiency24.io")
)

# Models
class ROICalculationRequest(BaseModel):
    # Campos de entrada
    consultas_mes: int = 500
    porcentaje_automatizacion_consultas: float = 70.0
    tiempo_respuesta_manual: float = 4.0
    horas_mensuales_crm: float = 40.0
    porcentaje_automatizacion_crm: float = 40.0
    numero_empleados: int = 3
    costo_horario_empleado: float = 2500.0
    costo_licencia_anual_bitrix: float = 150000.0
    costo_implementacion: float = 1000000.0
    
    # Campos opcionales
    valor_ticket_venta: Optional[float] = None
    tasa_conversion_actual: Optional[float] = None
    tasa_conversion_esperada: Optional[float] = None

class ContactForm(BaseModel):
    nombre_completo: str
    empresa: str
    telefono: Optional[str] = None
    email: EmailStr

class ROISubmission(BaseModel):
    calculo_roi: ROICalculationRequest
    contacto: ContactForm

class ROIResults(BaseModel):
    # Resultados de cálculo
    ahorro_tiempo_mensual_chatbot: float
    ahorro_economico_anual_chatbot: float
    ahorro_tiempo_anual_crm: float
    ahorro_economico_anual_crm: float
    ahorro_total_anual: float
    inversion_total: float
    roi_porcentaje: float
    ingresos_adicionales_estimados: Optional[float] = None

# Email Service
class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.gmail_user = settings.gmail_user
        self.gmail_password = settings.gmail_app_password

    def send_roi_results_email(
        self, 
        contacto: ContactForm,
        calculo: ROICalculationRequest,
        resultados: ROIResults
    ) -> bool:
        """Send email with ROI calculation results"""
        try:
            recipient_email = settings.recipient_email
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = recipient_email
            msg['Subject'] = f"Nueva Calculadora ROI - {contacto.empresa}"

            # Create HTML content
            html_content = self._create_roi_email_content(contacto, calculo, resultados)
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
                
            logger.info(f"ROI email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send ROI email: {str(e)}")
            return False

    def _create_roi_email_content(self, contacto: ContactForm, calculo: ROICalculationRequest, resultados: ROIResults) -> str:
        """Create formatted HTML email content for ROI results"""
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .logo {{ background-color: #007bff; color: white; padding: 10px 15px; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 18px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
                    .section h3 {{ color: #007bff; margin-top: 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                    th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; }}
                    th {{ background-color: #f8f9fa; font-weight: bold; }}
                    .highlight {{ background-color: #e8f4fd; font-weight: bold; }}
                    .footer {{ margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="logo">E24</div>
                    <h2>Nueva Calculadora ROI - Bitrix24 + Chatbot</h2>
                </div>
                
                <div class="section">
                    <h3>📋 Datos de Contacto</h3>
                    <table>
                        <tr><th>Nombre Completo</th><td>{contacto.nombre_completo}</td></tr>
                        <tr><th>Empresa</th><td>{contacto.empresa}</td></tr>
                        <tr><th>Email</th><td>{contacto.email}</td></tr>
        """
        
        if contacto.telefono:
            html_content += f"<tr><th>Teléfono</th><td>{contacto.telefono}</td></tr>"
        
        html_content += f"""
                    </table>
                </div>

                <div class="section">
                    <h3>📊 Parámetros de Entrada</h3>
                    <table>
                        <tr><th>Consultas de clientes por mes</th><td>{calculo.consultas_mes:,}</td></tr>
                        <tr><th>% consultas automatizables con chatbot</th><td>{calculo.porcentaje_automatizacion_consultas}%</td></tr>
                        <tr><th>Tiempo promedio respuesta manual (min)</th><td>{calculo.tiempo_respuesta_manual}</td></tr>
                        <tr><th>Horas mensuales tareas CRM</th><td>{calculo.horas_mensuales_crm}</td></tr>
                        <tr><th>% tareas CRM automatizables</th><td>{calculo.porcentaje_automatizacion_crm}%</td></tr>
                        <tr><th>Número de empleados</th><td>{calculo.numero_empleados}</td></tr>
                        <tr><th>Costo horario promedio (ARS)</th><td>${calculo.costo_horario_empleado:,.2f}</td></tr>
                        <tr><th>Costo licencia anual Bitrix24 (ARS)</th><td>${calculo.costo_licencia_anual_bitrix:,.2f}</td></tr>
                        <tr><th>Costo implementación (ARS)</th><td>${calculo.costo_implementacion:,.2f}</td></tr>
        """
        
        if calculo.valor_ticket_venta:
            html_content += f"""
                        <tr><th>Valor promedio ticket venta (ARS)</th><td>${calculo.valor_ticket_venta:,.2f}</td></tr>
                        <tr><th>Tasa conversión actual (%)</th><td>{calculo.tasa_conversion_actual}%</td></tr>
                        <tr><th>Tasa conversión esperada (%)</th><td>{calculo.tasa_conversion_esperada}%</td></tr>
            """
        
        html_content += f"""
                    </table>
                </div>

                <div class="section">
                    <h3>💰 Resultados del Cálculo ROI</h3>
                    <table>
                        <tr><th>Ahorro tiempo mensual chatbot (horas)</th><td>{resultados.ahorro_tiempo_mensual_chatbot:,.2f}</td></tr>
                        <tr><th>Ahorro económico anual chatbot (ARS)</th><td>${resultados.ahorro_economico_anual_chatbot:,.2f}</td></tr>
                        <tr><th>Ahorro tiempo anual CRM (horas)</th><td>{resultados.ahorro_tiempo_anual_crm:,.2f}</td></tr>
                        <tr><th>Ahorro económico anual CRM (ARS)</th><td>${resultados.ahorro_economico_anual_crm:,.2f}</td></tr>
                        <tr class="highlight"><th>Ahorro Total Anual (ARS)</th><td>${resultados.ahorro_total_anual:,.2f}</td></tr>
                        <tr class="highlight"><th>Inversión Total (ARS)</th><td>${resultados.inversion_total:,.2f}</td></tr>
                        <tr class="highlight"><th>ROI Estimado (%)</th><td>{resultados.roi_porcentaje:,.2f}%</td></tr>
        """
        
        if resultados.ingresos_adicionales_estimados:
            html_content += f"""
                        <tr class="highlight"><th>Ingresos Adicionales Estimados (ARS)</th><td>${resultados.ingresos_adicionales_estimados:,.2f}</td></tr>
            """
        
        html_content += f"""
                    </table>
                </div>

                <div class="footer">
                    <p><em>Este email fue enviado automáticamente desde la Calculadora ROI de Efficiency24.</em></p>
                    <p><strong>Fecha:</strong> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
            </body>
        </html>
        """
        
        return html_content

# Create global instance
email_service = EmailService()

# FastAPI app
app = FastAPI(title="Calculadora ROI Bitrix24 + Chatbot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate-roi")
async def calculate_roi(request: ROICalculationRequest) -> ROIResults:
    """Calculate ROI based on input parameters"""
    try:
        # Cálculo ahorro tiempo mensual chatbot (horas)
        consultas_automatizables = request.consultas_mes * (request.porcentaje_automatizacion_consultas / 100)
        tiempo_ahorro_mensual_chatbot = (consultas_automatizables * request.tiempo_respuesta_manual) / 60
        
        # Cálculo ahorro económico anual chatbot
        ahorro_economico_anual_chatbot = tiempo_ahorro_mensual_chatbot * 12 * request.costo_horario_empleado
        
        # Cálculo ahorro tiempo anual CRM (horas)
        tiempo_crm_automatizable = request.horas_mensuales_crm * (request.porcentaje_automatizacion_crm / 100)
        ahorro_tiempo_anual_crm = tiempo_crm_automatizable * 12 * request.numero_empleados
        
        # Cálculo ahorro económico anual CRM
        ahorro_economico_anual_crm = ahorro_tiempo_anual_crm * request.costo_horario_empleado
        
        # Ahorro total anual
        ahorro_total_anual = ahorro_economico_anual_chatbot + ahorro_economico_anual_crm
        
        # Inversión total
        inversion_total = request.costo_implementacion + request.costo_licencia_anual_bitrix
        
        # ROI porcentaje
        roi_porcentaje = ((ahorro_total_anual - inversion_total) / inversion_total) * 100 if inversion_total > 0 else 0
        
        # Ingresos adicionales estimados (opcional)
        ingresos_adicionales_estimados = None
        if (request.valor_ticket_venta and 
            request.tasa_conversion_actual is not None and 
            request.tasa_conversion_esperada is not None):
            
            mejora_conversion = request.tasa_conversion_esperada - request.tasa_conversion_actual
            leads_mensuales_estimados = request.consultas_mes * 0.3  # Asumimos 30% de consultas son leads potenciales
            ingresos_adicionales_estimados = (leads_mensuales_estimados * 12 * 
                                           (mejora_conversion / 100) * 
                                           request.valor_ticket_venta)
        
        return ROIResults(
            ahorro_tiempo_mensual_chatbot=round(tiempo_ahorro_mensual_chatbot, 2),
            ahorro_economico_anual_chatbot=round(ahorro_economico_anual_chatbot, 2),
            ahorro_tiempo_anual_crm=round(ahorro_tiempo_anual_crm, 2),
            ahorro_economico_anual_crm=round(ahorro_economico_anual_crm, 2),
            ahorro_total_anual=round(ahorro_total_anual, 2),
            inversion_total=round(inversion_total, 2),
            roi_porcentaje=round(roi_porcentaje, 2),
            ingresos_adicionales_estimados=round(ingresos_adicionales_estimados, 2) if ingresos_adicionales_estimados else None
        )
        
    except Exception as e:
        logger.error(f"Error calculating ROI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en cálculo ROI: {str(e)}")

@app.post("/api/submit-roi")
async def submit_roi(
    submission: ROISubmission,
    background_tasks: BackgroundTasks
):
    """Submit ROI calculation and send email"""
    try:
        # Calculate ROI results
        results = await calculate_roi(submission.calculo_roi)
        
        # Add email sending to background tasks
        background_tasks.add_task(
            email_service.send_roi_results_email,
            submission.contacto,
            submission.calculo_roi,
            results
        )
        
        return {
            "success": True,
            "message": "Sus resultados están en camino! En breve te contactaremos."
        }
        
    except Exception as e:
        logger.error(f"Error submitting ROI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al enviar formulario: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "roi-calculator",
        "smtp_configured": bool(settings.gmail_user and settings.gmail_app_password)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)