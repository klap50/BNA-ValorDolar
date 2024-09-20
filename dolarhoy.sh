#!/bin/bash

# Endpoint de la API
URL="https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/4/2024-02-01/2024-02-05"

# Hacer la consulta con curl y usar jq para procesar el JSON
response=$(curl -sk "$URL")

# Crear el archivo CSV
echo "Fecha,Valor" > cambio.csv

# Usar jq para extraer los valores de fecha y valor
echo "$response" | jq -r '.results[] | "\(.fecha),\(.valor)"' >> cambio.csv

echo "Archivo CSV creado: cambio.csv"
