{{/*
Expand the name of the chart.
*/}}
{{- define "chaincommand.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "chaincommand.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chaincommand.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chaincommand.labels" -}}
helm.sh/chart: {{ include "chaincommand.chart" . }}
{{ include "chaincommand.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chaincommand.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chaincommand.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "chaincommand.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "chaincommand.fullname" .) }}
{{- else }}
{{- printf "localhost" }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "chaincommand.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "chaincommand.fullname" .) }}
{{- else }}
{{- printf "localhost" }}
{{- end }}
{{- end }}
