# 🚀 Configuración del Chatbot con Groq

## ¿Por qué Groq?

**Groq es la mejor opción para APIs de IA gratuitas:**

- ✅ **100% GRATIS** - Sin tarjeta de crédito
- ✅ **14,000+ tokens/minuto** - Límite muy generoso
- ✅ **Ultra rápido** - Hasta 7.41x más rápido que otras APIs
- ✅ **Modelos open source** - Llama 3.3, Mixtral, Gemma
- ✅ **Compatible con OpenAI** - Fácil de integrar
- ✅ **Sin cuotas restrictivas** - No como Gemini (429 errors)

---

## 📝 Cómo obtener tu API Key GRATIS

### Paso 1: Crear cuenta en Groq

1. Ve a **[https://console.groq.com](https://console.groq.com)**
2. Haz clic en **"Sign Up"** o **"Get Started"**
3. Regístrate con:
   - Email
   - Google
   - GitHub

### Paso 2: Generar API Key

1. Una vez dentro, ve a **[https://console.groq.com/keys](https://console.groq.com/keys)**
2. Haz clic en **"Create API Key"**
3. Dale un nombre (ej: "Dashboard Retail")
4. **Copia tu API key** - se verá como: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
5. ⚠️ **¡Guárdala!** - No la podrás ver de nuevo

### Paso 3: Usar en el Dashboard

1. Abre el dashboard en [http://localhost:8501](http://localhost:8501)
2. En el **sidebar izquierdo**, expande **"⚙️ Configurar API Key de Groq"**
3. Pega tu API key (empieza con `gsk_...`)
4. El chatbot se inicializará automáticamente
5. **¡Listo!** Ahora puedes hacer preguntas

---

## 💬 Ejemplo de uso del Chatbot

**Preguntas que puedes hacer:**

- ¿Qué estrategia recomiendas para el segmento Champions?
- ¿Cuál es el segmento más valioso?
- ¿Cómo puedo recuperar clientes At Risk?
- Explícame las métricas RFM
- ¿Qué acciones tomar para aumentar la frecuencia de compra?
- Compara Champions vs Loyal Customers

---

## 🔧 Solución de problemas

### Error: "No se pudo conectar con ningún modelo"

**Solución:**
- Verifica que tu API key sea correcta (empieza con `gsk_`)
- Revisa tu conexión a internet
- Intenta generar una nueva API key

### El chatbot no aparece

**Solución:**
1. Asegúrate de haber instalado groq: `pip install groq`
2. Reinicia el dashboard
3. Ingresa tu API key en el sidebar

### Respuestas lentas

**Solución:**
- Es normal la primera vez (inicialización)
- Groq es generalmente muy rápido (< 2 segundos)
- Si persiste, prueba con otro modelo usando el botón "Ver Modelos Disponibles"

---

## 📊 Modelos disponibles en Groq

El dashboard probará automáticamente estos modelos en orden:

1. **llama-3.3-70b-versatile** ⭐ *Recomendado* - Mejor balance
2. **llama-3.1-70b-versatile** - Muy capaz
3. **mixtral-8x7b-32768** - Context window grande
4. **gemma2-9b-it** - Rápido y eficiente
5. **llama3-70b-8192** - Robusto
6. **llama3-8b-8192** - Más rápido

---

## 🆚 Comparación: Groq vs Gemini

| Característica | Groq | Gemini |
|----------------|------|---------|
| Precio | **GRATIS** | Gratis limitado |
| Límite requests | **14K tokens/min** | ~60 requests/min |
| Velocidad | **Ultra rápido** | Normal |
| Errores 429 | **Rarísimos** | Frecuentes |
| Tarjeta requerida | **NO** | No |
| Setup | **2 minutos** | 5 minutos |
| Estabilidad | **Alta** | Media |

---

## 📚 Recursos adicionales

- **Documentación oficial:** [https://console.groq.com/docs](https://console.groq.com/docs)
- **Comunidad:** [https://discord.gg/groq](https://discord.gg/groq)
- **Ejemplos:** [https://github.com/groq/groq-python](https://github.com/groq/groq-python)

---

## ✅ Checklist de configuración

- [ ] Crear cuenta en Groq Console
- [ ] Generar API key
- [ ] Copiar API key (empieza con `gsk_...`)
- [ ] Abrir dashboard (localhost:8501)
- [ ] Pegar API key en sidebar
- [ ] Ver "✓ Conectado con: llama-3.3-70b-versatile"
- [ ] Hacer primera pregunta al chatbot
- [ ] **¡Disfrutar!** 🎉

---

**Nota:** Tu API key no se guarda en ningún archivo, solo se usa durante la sesión actual del dashboard.
