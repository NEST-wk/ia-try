# Script de Configuración Rápida - Segmentación de Clientes
# ==========================================================

Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Segmentación de Clientes - Setup Rápido" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "`n"

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python no encontrado. Por favor instala Python 3.8+." -ForegroundColor Red
    exit 1
}

# Crear entorno virtual
Write-Host "`n[2/5] Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Entorno virtual ya existe" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "  ✓ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "`n[3/5] Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "  ✓ Entorno virtual activado" -ForegroundColor Green

# Instalar dependencias
Write-Host "`n[4/5] Instalando dependencias..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "  ✓ Dependencias instaladas" -ForegroundColor Green

# Verificar dataset
Write-Host "`n[5/5] Verificando dataset..." -ForegroundColor Yellow
if (Test-Path "data\Online Retail.xlsx") {
    Write-Host "  ✓ Dataset encontrado" -ForegroundColor Green
} else {
    Write-Host "  ⚠  Dataset no encontrado" -ForegroundColor Yellow
    Write-Host "     Descárgalo desde: https://archive.ics.uci.edu/ml/datasets/Online+Retail" -ForegroundColor Yellow
    Write-Host "     Y colócalo en: data\Online Retail.xlsx" -ForegroundColor Yellow
}

# Resumen
Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Completado" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nPróximos pasos:" -ForegroundColor White
Write-Host "  1. Asegúrate de tener el dataset en data\Online Retail.xlsx" -ForegroundColor White
Write-Host "  2. Ejecutar análisis:" -ForegroundColor White
Write-Host "     jupyter notebook notebooks/analisis_segmentacion.ipynb" -ForegroundColor Cyan
Write-Host "  3. Ejecutar dashboard:" -ForegroundColor White
Write-Host "     streamlit run src/app_dashboard.py" -ForegroundColor Cyan

Write-Host "`n✓ Todo listo para comenzar!`n" -ForegroundColor Green
