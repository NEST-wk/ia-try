# 🎯 Guía Rápida - Chatbot con Groq

## ¿Qué es Groq y por qué es mejor?

**Groq** es una plataforma de IA que ofrece acceso **GRATIS** a modelos de lenguaje open source como:
- 🦙 **Llama 3.3 70B** - El más potente
- 🎭 **Mixtral 8x7B** - Excelente para múltiples tareas
- 💎 **Gemma 2 9B** - Rápido y eficiente

### Ventajas sobre Gemini:
- ✅ **Sin errores 429** (quota exceeded)
- ✅ **Sin errores 404** (model not found)
- ✅ **14,000 tokens/minuto** vs 60 requests/min de Gemini
- ✅ **7.41x más rápido** según benchmarks
- ✅ **100% gratis** sin restricciones

---

## 📸 Tutorial Visual Paso a Paso

### Paso 1: Abrir Groq Console

1. Abre tu navegador
2. Ve a: **https://console.groq.com**
3. Verás la página principal de Groq

### Paso 2: Crear Cuenta (30 segundos)

Opciones de registro:
- **Email** → Ingresa tu email + contraseña
- **Google** → Clic en "Sign in with Google"
- **GitHub** → Clic en "Sign in with GitHub"

👉 **Recomendado:** Usa Google para registro instantáneo

### Paso 3: Generar API Key

1. Una vez dentro, ve al menú lateral izquierdo
2. Haz clic en **"API Keys"**
3. O ve directo a: **https://console.groq.com/keys**
4. Haz clic en el botón **"Create API Key"**
5. Dale un nombre descriptivo (ej: "Dashboard Retail")
6. Haz clic en **"Submit"**
7. **¡IMPORTANTE!** Copia tu API key **AHORA**
   - Se verá como: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - No podrás verla de nuevo después

### Paso 4: Guardar tu API Key

**Opciones:**

**A) En un archivo de texto:**
```
Groq API Key: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Fecha: 18/12/2024
Proyecto: Dashboard Retail
```

**B) En tu administrador de contraseñas** (más seguro)

**C) Copiar directo al dashboard** (si lo usarás ahora)

### Paso 5: Usar en el Dashboard

1. Abre el dashboard: **http://localhost:8501**
2. Mira el **sidebar izquierdo** (barra lateral)
3. Busca la sección **"⚙️ Configurar API Key de Groq"**
4. Haz clic para expandir
5. En el campo **"Groq API Key"**:
   - Pega tu API key (Ctrl+V)
   - Debe empezar con `gsk_`
6. Espera 2-3 segundos
7. Verás: **"✓ Conectado con: llama-3.3-70b-versatile"**

### Paso 6: ¡Hacer tu Primera Pregunta!

**Ejemplos de preguntas:**

```
¿Cuál es el segmento más valioso?
```

```
¿Qué estrategia recomiendas para recuperar clientes At Risk?
```

```
Explícame las diferencias entre Champions y Loyal Customers
```

```
¿Cómo puedo aumentar la frecuencia de compra?
```

```
Resume los insights principales de mi base de clientes
```

---

## 🔍 Verificar que Funciona

### ✅ Señales de éxito:

1. **En el sidebar:**
   - ✓ Conectado con: llama-3.3-70b-versatile

2. **Aparece la caja de texto:**
   - "💬 Hazme una pregunta:"

3. **Botones visibles:**
   - 📤 Enviar
   - 🗑️ (limpiar historial)

### ❌ Si algo sale mal:

**Error: "No se pudo conectar"**
- Verifica tu API key
- Asegúrate que empiece con `gsk_`
- Revisa tu conexión a internet
- Genera una nueva API key

**El chatbot no aparece**
- Asegúrate de expandir "⚙️ Configurar API Key de Groq"
- Verifica que Streamlit esté corriendo
- Refresca la página (F5)

**Respuesta lenta la primera vez**
- Es normal (inicialización)
- Siguientes respuestas serán rápidas (< 2s)

---

## 💡 Tips de Uso

### Preguntas más efectivas:

**❌ Mal:**
```
dime algo
```

**✅ Bien:**
```
¿Qué acciones específicas recomiendas para aumentar 
el valor de vida del cliente (CLV) en el segmento 
Loyal Customers?
```

### El chatbot conoce:

- ✓ Total de clientes
- ✓ Número de segmentos
- ✓ Nombres de segmentos
- ✓ Métricas RFM promedio
- ✓ Contribución de cada segmento a ingresos
- ✓ Estrategias de marketing y retención

### El chatbot NO puede (todavía):

- ✗ Ver gráficas directamente
- ✗ Modificar segmentos
- ✗ Acceder a datos fuera del análisis actual
- ✗ Ejecutar código Python

---

## 🎓 Ejemplos de Conversación

### Ejemplo 1: Análisis Estratégico

**Tú:**
```
¿Qué segmento debería priorizar con mi presupuesto 
de marketing limitado?
```

**Asistente:**
```
Basándome en los datos actuales:

Champions (15% de clientes, 45% de ingresos):
- ROI más alto
- Ya son leales, necesitan menor inversión
- Estrategia: Programas VIP, early access

At Risk (20% de clientes):
- Segundo en prioridad
- Alto riesgo de pérdida
- Estrategia: Campañas de recuperación urgentes

Recomendación: 60% Champions, 40% At Risk
```

### Ejemplo 2: Interpretación de Métricas

**Tú:**
```
Explícame por qué la Recency es importante
```

**Asistente:**
```
Recency mide días desde la última compra:

- Baja Recency (< 50 días): Cliente activo, 
  alta probabilidad de recompra
  
- Alta Recency (> 200 días): Cliente inactivo,
  riesgo de abandono

Es la métrica más predictiva porque:
1. Clientes recientes están "calientes"
2. A más días, menor engagement
3. Indica el momento ideal para reactivación
```

---

## 🆘 Soporte

**¿Problemas con Groq?**
- Discord: https://discord.gg/groq
- Docs: https://console.groq.com/docs

**¿Problemas con el Dashboard?**
- Revisa los logs de Streamlit
- Verifica requirements.txt
- Asegúrate que groq==0.11.0 esté instalado

---

## 📊 Estadísticas de Groq (Diciembre 2024)

- 🌍 **2.7M+ desarrolladores** usando Groq
- ⚡ **Velocidad promedio:** < 2 segundos
- 🎯 **Precisión:** Comparable a GPT-4
- 💰 **Costo para ti:** $0.00

---

**¡Disfruta tu nuevo asistente IA! 🚀**
