# 💬 Chat Flotante - Guía de Uso

## 🎉 Nueva Funcionalidad: Chat Flotante con Popover

El chatbot ahora aparece en un **popover flotante en la esquina inferior derecha** que **NO tapa la pantalla** y es mucho más cómodo que el sidebar con scroll.

---

## ✨ Ventajas del Nuevo Chat

### Antes (Sidebar con scroll):
- ❌ Scroll infinito fastidioso
- ❌ Espacio limitado
- ❌ Difícil ver conversaciones largas
- ❌ Oculta otros controles

### Ahora (Popover Flotante):
- ✅ **Flota en esquina inferior derecha**
- ✅ **NO tapa el contenido** - puedes seguir viendo todo
- ✅ **Scroll independiente** (350px de altura)
- ✅ **Siempre accesible** mientras navegas
- ✅ **Mensajes con estilo chat moderno** (burbujas)
- ✅ **Compacto pero funcional**

---

## 🚀 Cómo Usar el Chat Flotante

### Paso 1: Configurar API Key

1. En el **sidebar**, expande **"⚙️ Configurar API Key de Groq"**
2. Pega tu API key de Groq (obtén una gratis en [console.groq.com/keys](https://console.groq.com/keys))
3. Espera a ver: **"✓ Conectado con: llama-3.3-70b-versatile"**

### Paso 2: Abrir el Chat

1. En el **sidebar**, aparecerá el botón **"💬 Abrir Chat Flotante"**
2. Haz clic en él
3. Aparecerá un **ícono 💬 en la esquina inferior derecha**

### Paso 3: Usar el Chat

1. Haz clic en el **ícono 💬** flotante
2. Se despliega un **popover** con el chat completo
3. **Importante:** El popover **NO tapa la pantalla** - puedes seguir viendo todo el dashboard

### Paso 4: Chatear

1. **Escribe tu pregunta** en el área de texto
2. Haz clic en **"📤 Enviar"**
3. Espera la respuesta (aparecerá en 2-3 segundos)
4. Los mensajes se muestran con **burbujas de chat**:
   - 👤 Tú: burbujas a la derecha
   - 🤖 Asistente: burbujas a la izquierda

### Paso 5: Gestionar la Conversación

**Scroll de mensajes:**
- El popover tiene un área scrolleable de **350px**
- Puedes ver toda la conversación
- El dashboard permanece visible detrás

**Limpiar historial:**
- Clic en **"🗑️"** para borrar todos los mensajes
- Útil para empezar una nueva conversación

**Cerrar popover:**
- Haz clic fuera del popover
- O en el botón **"❌ Cerrar Chat"**
- Tu historial se mantiene

**Seguir navegando:**
- El chat permanece abierto mientras navegas por las pestañas
- Puedes hacer preguntas mientras ves las gráficas

### Paso 6: Reabrir

1. Haz clic de nuevo en el **ícono 💬** flotante
2. Tu conversación anterior estará allí
3. Continúa donde lo dejaste

---

## 💡 Características del Chat Flotante

### Diseño No Intrusivo:
- 🎯 **Esquina inferior derecha** - no estorba
- 👁️ **NO tapa el contenido** - dashboard siempre visible
- 📦 **Popover compacto** - aparece cuando lo necesitas
- 🔄 **Scroll independiente** - 350px dedicados al chat
- 💬 **Estilo chat app** - como WhatsApp/Telegram
- 🌈 **Avatares**: 👤 para ti, 🤖 para el asistente

### Información en el Popover:
- **Título**: "🤖 Asistente IA"
- **Modelo activo**: Muestra qué modelo de Groq está usando
- **Botón cerrar**: Para ocultar el popover
- **Estado de carga**: Spinner mientras piensa

### Área de Conversación:
- **Height fija**: 350px con scroll automático
- **Chat messages**: Componentes nativos de Streamlit
- **Formato claro**: Separa tus mensajes de las respuestas
- **Sin límite**: Todas las conversaciones disponibles
- **Transparencia**: Puedes ver el dashboard detrás

---

## 🎯 Ejemplos de Uso

### Conversación Simple:

**Tú:** ¿Cuál es el segmento más valioso?

**Asistente:** Basándome en los datos, el segmento **Champions** es el más valioso...

---

### Conversación Larga:

Puedes hacer múltiples preguntas seguidas sin que el scroll del dashboard se vea afectado:

1. ¿Qué estrategia recomiendas para Champions?
2. ¿Y para At Risk?
3. Explícame las diferencias entre Recency y Frequency
4. ¿Cómo interpretar la matriz de confusión?

Todo visible en la **ventana de 400px** con scroll independiente.

---

## 🔧 Funcionalidades Técnicas

### Estados Guardados:
- `st.session_state.chat_open`: Controla si la ventana está abierta
- `st.session_state.chat_history`: Guarda todos los mensajes
- `st.session_state.groq_client`: Mantiene la conexión con Groq
- `st.session_state.groq_model`: Modelo activo

### Componentes Usados:
- `@st.dialog`: Decorador para crear la ventana modal
- `st.chat_message`: Burbujas de chat nativas de Streamlit
- `st.container(height=400)`: Área scrolleable fija
- `st.spinner`: Indicador de carga durante la respuesta

---

## 🎨 Personalización Visual

### Mensajes del Usuario:
- Avatar: 👤
- Posición: Derecha (implícito en chat_message)
- Color: Predeterminado de Streamlit

### Mensajes del Asistente:
- Avatar: 🤖
- Posición: Izquierda
- Color: Predeterminado de Streamlit

### Ventana Modal:
- Ancho: `width="large"` (más espacio)
- Título: "💬 Asistente IA"
- Botones: Primary (azul) para enviar

---

## 📱 Responsive

La ventana modal se adapta a diferentes tamaños de pantalla:
- **Desktop**: Ventana grande centrada
- **Tablet**: Ventana media centrada
- **Mobile**: Fullscreen modal

---

## 🐛 Troubleshooting

### La ventana no se abre:

**Problema:** Hago clic en "Abrir Chat" pero no pasa nada

**Solución:**
1. Verifica que tu API key esté configurada
2. Revisa que veas "✓ Conectado con..."
3. Refresca la página (F5)
4. Verifica la consola del navegador (F12)

### Los mensajes no aparecen:

**Problema:** Envío mensajes pero no se muestran

**Solución:**
1. Verifica que el spinner "🤔 Pensando..." aparezca
2. Espera a ver "✓ Respuesta recibida"
3. Si hay error, se mostrará en rojo
4. Revisa tu conexión a internet

### Scroll no funciona:

**Problema:** No puedo hacer scroll en los mensajes

**Solución:**
1. Asegúrate de hacer scroll **dentro** de la ventana
2. El contenedor tiene 400px de altura
3. Prueba con la rueda del mouse o trackpad

---

## ⚡ Tips Pro

### 1. Mantén el chat abierto mientras exploras
- Haz clic en el ícono 💬 para abrir el popover
- **Explora las pestañas con el chat abierto**
- Haz preguntas mientras ves las gráficas
- El popover flota sobre el contenido SIN taparlo

### 2. Cierra/abre rápidamente
- Haz clic fuera del popover para cerrarlo
- Haz clic en 💬 para reabrirlo
- Tu historial siempre se mantiene
- Perfecto para consultas rápidas

### 3. Usa el historial
- No borres mensajes si quieres contexto
- El asistente no "recuerda" mensajes anteriores (stateless)
- Pero tú puedes ver todo el historial scrolleando

### 4. Preguntas efectivas
- **Específicas**: "¿Qué estrategia para Champions?" en vez de "dime algo"
- **Con contexto**: "Basándome en las métricas RFM, ¿qué segmento priorizar?"
- **Comparativas**: "Compara Champions vs Loyal Customers"
- **Mientras ves datos**: "Explícame este gráfico de segmentos"

### 5. Limpia cuando cambies de tema
- Si cambias de tema completamente
- Haz clic en "🗑️"
- Empiezas fresh con un nuevo contexto

---

## 🎓 Keyboard Shortcuts

*Próximamente se pueden agregar:*
- `Ctrl + Enter`: Enviar mensaje
- `Esc`: Cerrar ventana
- `Ctrl + L`: Limpiar historial

---

## 📊 Comparativa: Sidebar vs Popover Flotante

| Característica | Sidebar | Popover Flotante |
|----------------|---------|------------------|
| Espacio disponible | ~300px | ~400px |
| Scroll independiente | ❌ No | ✅ Sí |
| Altura fija | ❌ Crece | ✅ 350px |
| Tapa contenido | ⚠️ Empuja | ❌ **NO tapa** |
| Oculta controles | ✅ Sí | ❌ **NO** |
| Ver dashboard mientras chateas | ❌ No | ✅ **Sí** |
| Posición | Izquierda fija | Esquina inferior derecha |
| Fácil de encontrar | ❌ Scroll | ✅ Ícono flotante |
| Estilo moderno | ❌ Básico | ✅ Chat app |
| Mobile friendly | ⚠️ Medio | ✅ Sí |

---

## 🚀 Próximas Mejoras

**En consideración:**
- ⭐ Exportar conversación a PDF
- ⭐ Búsqueda dentro del historial
- ⭐ Sugerencias de preguntas automáticas
- ⭐ Modo oscuro para el chat
- ⭐ Shortcuts de teclado
- ⭐ Notificación sonora cuando responde

---

**¡Disfruta del nuevo chat flotante! 💬🚀**

*Mucho más cómodo que el scroll infinito del sidebar.*
