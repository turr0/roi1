import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  // Estados para los campos de entrada
  const [formData, setFormData] = useState({
    consultas_mes: 500,
    porcentaje_automatizacion_consultas: 70.0,
    tiempo_respuesta_manual: 4.0,
    horas_mensuales_crm: 40.0,
    porcentaje_automatizacion_crm: 40.0,
    numero_empleados: 3,
    costo_horario_empleado: 2500.0,
    costo_licencia_anual_bitrix: 150000.0,
    costo_implementacion: 1000000.0,
    valor_ticket_venta: '',
    tasa_conversion_actual: '',
    tasa_conversion_esperada: ''
  });

  // Estados para el formulario de contacto
  const [contactData, setContactData] = useState({
    nombre_completo: '',
    empresa: '',
    telefono: '',
    email: ''
  });

  // Estados de UI
  const [showContactForm, setShowContactForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? '' : parseFloat(value) || value
    }));
  };

  const handleContactChange = (e) => {
    const { name, value } = e.target;
    setContactData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateContactForm = () => {
    const newErrors = {};
    
    if (!contactData.nombre_completo.trim()) {
      newErrors.nombre_completo = 'El nombre completo es requerido';
    }
    
    if (!contactData.empresa.trim()) {
      newErrors.empresa = 'La empresa es requerida';
    }
    
    if (!contactData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(contactData.email)) {
      newErrors.email = 'El email no es válido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCalculateROI = () => {
    setShowContactForm(true);
  };

  const handleSubmitROI = async (e) => {
    e.preventDefault();
    
    if (!validateContactForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Preparar datos para envío
      const submissionData = {
        calculo_roi: {
          ...formData,
          valor_ticket_venta: formData.valor_ticket_venta || null,
          tasa_conversion_actual: formData.tasa_conversion_actual || null,
          tasa_conversion_esperada: formData.tasa_conversion_esperada || null
        },
        contacto: contactData
      };

      const response = await axios.post(`${API_BASE_URL}/api/submit-roi`, submissionData);
      
      if (response.data.success) {
        setSubmitSuccess(true);
      }
      
    } catch (error) {
      console.error('Error submitting ROI:', error);
      alert('Error al enviar el formulario. Por favor, inténtelo de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-blue-600 text-white rounded-lg flex items-center justify-center text-xl font-bold mx-auto mb-6">
            E24
          </div>
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">¡Sus resultados están en camino!</h2>
          <p className="text-gray-600 mb-6">En breve te contactaremos con el análisis detallado de ROI personalizado para su empresa.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Nueva Calculadora
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center text-lg font-bold">
              E24
            </div>
            <h1 className="text-2xl font-bold text-gray-800">Calculadora ROI - Bitrix24 + Chatbot</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Estadísticas educativas */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-blue-800 mb-4">📊 Datos clave sobre automatización</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold text-blue-700 mb-2">Chatbots</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Automatizan entre 60% y 80% de consultas (IBM, Intercom)</li>
                <li>• Tiempo promedio de respuesta manual: 3-5 minutos</li>
              </ul>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold text-blue-700 mb-2">CRM Automatización</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Reduce carga administrativa 30%-50% (Nucleus Research)</li>
                <li>• Optimiza tareas, seguimientos y reportes</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Formulario principal */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Parámetros de su empresa</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* Chatbot */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-blue-600 border-b border-blue-100 pb-2">
                🤖 Chatbot
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Consultas de clientes por mes
                </label>
                <input
                  type="number"
                  name="consultas_mes"
                  value={formData.consultas_mes}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  % consultas automatizables con chatbot
                </label>
                <input
                  type="range"
                  name="porcentaje_automatizacion_consultas"
                  min="0"
                  max="100"
                  step="5"
                  value={formData.porcentaje_automatizacion_consultas}
                  onChange={handleInputChange}
                  className="w-full"
                />
                <div className="text-right text-sm text-blue-600 font-semibold">
                  {formData.porcentaje_automatizacion_consultas}%
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tiempo promedio respuesta manual (minutos)
                </label>
                <input
                  type="number"
                  name="tiempo_respuesta_manual"
                  value={formData.tiempo_respuesta_manual}
                  onChange={handleInputChange}
                  step="0.5"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* CRM */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-blue-600 border-b border-blue-100 pb-2">
                ⚙️ CRM Bitrix24
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Horas mensuales en tareas manuales CRM
                </label>
                <input
                  type="number"
                  name="horas_mensuales_crm"
                  value={formData.horas_mensuales_crm}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  % tareas CRM automatizables
                </label>
                <input
                  type="range"
                  name="porcentaje_automatizacion_crm"
                  min="0"
                  max="100"
                  step="5"
                  value={formData.porcentaje_automatizacion_crm}
                  onChange={handleInputChange}
                  className="w-full"
                />
                <div className="text-right text-sm text-blue-600 font-semibold">
                  {formData.porcentaje_automatizacion_crm}%
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número de empleados involucrados
                </label>
                <input
                  type="number"
                  name="numero_empleados"
                  value={formData.numero_empleados}
                  onChange={handleInputChange}
                  min="1"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Costos */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-blue-600 mb-4">💰 Costos</h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Costo horario promedio por empleado (ARS)
                </label>
                <input
                  type="number"
                  name="costo_horario_empleado"
                  value={formData.costo_horario_empleado}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Costo licencia anual Bitrix24 (ARS)
                </label>
                <input
                  type="number"
                  name="costo_licencia_anual_bitrix"
                  value={formData.costo_licencia_anual_bitrix}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Costo fijo de implementación (ARS)
              </label>
              <input
                type="number"
                name="costo_implementacion"
                value={formData.costo_implementacion}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                readOnly
              />
              <p className="text-xs text-gray-500 mt-1">Valor fijo establecido</p>
            </div>
          </div>

          {/* Campos opcionales */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-blue-600 mb-4">📈 Ingresos adicionales (Opcional)</h3>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Valor promedio ticket venta (ARS)
                </label>
                <input
                  type="number"
                  name="valor_ticket_venta"
                  value={formData.valor_ticket_venta}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Opcional"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tasa conversión actual (%)
                </label>
                <input
                  type="number"
                  name="tasa_conversion_actual"
                  value={formData.tasa_conversion_actual}
                  onChange={handleInputChange}
                  step="0.1"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Opcional"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tasa conversión esperada con chatbot (%)
                </label>
                <input
                  type="number"
                  name="tasa_conversion_esperada"
                  value={formData.tasa_conversion_esperada}
                  onChange={handleInputChange}
                  step="0.1"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Opcional"
                />
              </div>
            </div>
          </div>

          {/* Botón calcular */}
          <div className="mt-8 text-center">
            <button
              onClick={handleCalculateROI}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
            >
              Calcular ROI 📊
            </button>
          </div>
        </div>

        {/* Formulario de contacto */}
        {showContactForm && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-6">
              📋 Complete sus datos para recibir el análisis
            </h2>
            <p className="text-gray-600 mb-6">
              Sus resultados serán enviados directamente a su email junto con un análisis personalizado de nuestro equipo.
            </p>

            <form onSubmit={handleSubmitROI}>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre completo *
                  </label>
                  <input
                    type="text"
                    name="nombre_completo"
                    value={contactData.nombre_completo}
                    onChange={handleContactChange}
                    className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.nombre_completo ? 'border-red-300' : 'border-gray-300'
                    }`}
                    required
                  />
                  {errors.nombre_completo && (
                    <p className="text-red-500 text-xs mt-1">{errors.nombre_completo}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Empresa *
                  </label>
                  <input
                    type="text"
                    name="empresa"
                    value={contactData.empresa}
                    onChange={handleContactChange}
                    className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.empresa ? 'border-red-300' : 'border-gray-300'
                    }`}
                    required
                  />
                  {errors.empresa && (
                    <p className="text-red-500 text-xs mt-1">{errors.empresa}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Teléfono
                  </label>
                  <input
                    type="tel"
                    name="telefono"
                    value={contactData.telefono}
                    onChange={handleContactChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Opcional"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={contactData.email}
                    onChange={handleContactChange}
                    className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.email ? 'border-red-300' : 'border-gray-300'
                    }`}
                    required
                  />
                  {errors.email && (
                    <p className="text-red-500 text-xs mt-1">{errors.email}</p>
                  )}
                </div>
              </div>

              <div className="mt-6 text-center">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`px-8 py-3 rounded-lg text-lg font-semibold transition-colors shadow-lg ${
                    isSubmitting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isSubmitting ? 'Enviando...' : 'Enviar Análisis ROI 📧'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center text-lg font-bold mx-auto mb-4">
            E24
          </div>
          <p className="text-gray-300">
            Calculadora ROI especializada para PYMES argentinas - Efficiency24
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;