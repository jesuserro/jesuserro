# Manual rápido de SOPS + age para RenderCV

Este manual resume un flujo sencillo y práctico para guardar datos privados (como `email` y `phone`) cifrados en Git, y generar después el YAML final que RenderCV necesita.

## 1. Qué es cada pieza

- **age**: herramienta moderna y simple de cifrado por clave pública/privada.
- **SOPS**: herramienta para editar, cifrar y descifrar secretos en formatos como YAML, JSON, ENV/dotenv e INI.
- **RenderCV**: no interpola variables `${...}` por sí mismo; necesita recibir un YAML ya resuelto.

## 2. Qué archivos usarás

Estructura recomendada del proyecto:

```text
/home/name/proyectos/name/
├── .sops.yaml
├── .env.enc
├── .gitignore
├── render.sh
└── cv/
    ├── Jesus_Erro_CV.template.yaml
    └── Jesus_Erro_CV.yaml
```

Qué va a Git:
- `.sops.yaml`
- `.env.enc`
- `render.sh`
- `cv/Jesus_Erro_CV.template.yaml`

Qué NO va a Git:
- `.env`
- `cv/Jesus_Erro_CV.yaml`
- `~/.config/sops/age/keys.txt`

## 3. Instalación

En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y age gettext-base curl
```

- `age`: cifrado
- `gettext-base`: trae `envsubst`
- `curl`: útil para descargar binarios si hace falta

### Instalar SOPS

A veces `sops` no está en APT. Si ya lo tienes instalado, compruébalo:

```bash
which sops
sops --version
```

Si no estuviera instalado, puedes usar el `.deb` oficial:

```bash
SOPS_VERSION=3.12.1
ARCH=amd64

curl -LO https://github.com/getsops/sops/releases/download/v${SOPS_VERSION}/sops_${SOPS_VERSION}_${ARCH}.deb
sudo dpkg -i sops_${SOPS_VERSION}_${ARCH}.deb
```

## 4. Comprobar o reutilizar tu clave age

Si ya tienes una clave para otros proyectos, **reutilízala**. No sobrescribas `keys.txt`.

Comprobar el fichero:

```bash
ls -la ~/.config/sops/age
```

Ver la **clave pública**:

```bash
grep '^# public key:' ~/.config/sops/age/keys.txt
```

Eso devuelve algo como:

```text
# public key: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

La **public key** (`age1...`) sí puede ir en `.sops.yaml`.

La **private key** (`AGE-SECRET-KEY-...`) **nunca** debe ir a Git.

### Si no tuvieras clave aún

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
```

## 5. Crear `.sops.yaml`

Ponlo en la **raíz del proyecto**, no en `/home/name`.

Ejemplo:

```yaml
creation_rules:
  - path_regex: ^\.env\.enc$
    age: age1TU_PUBLIC_KEY_AQUI
```

Importante:
- `path_regex` debe coincidir con el nombre lógico del archivo cifrado.
- En este manual usamos `.env.enc`.

## 6. Crear el secreto temporal `.env`

Ejemplo con email y teléfono:

```bash
cat > .env <<'EOF'
CV_EMAIL="name@company.com"
CV_PHONE="100 123 456"
EOF
```

## 7. Cifrar `.env` a `.env.enc`

Este es el punto más poco intuitivo de SOPS:

**La redirección `> .env.enc` la maneja el shell, no SOPS.**
Por eso, para que SOPS aplique la regla de `.sops.yaml`, hay que usar `--filename-override`.

Comando correcto:

```bash
rm -f .env.enc
sops encrypt \
  --filename-override .env.enc \
  --input-type dotenv \
  --output-type dotenv \
  .env > .env.enc
```

## 8. Validar que el cifrado está bien

```bash
sops --decrypt --input-type dotenv --output-type dotenv .env.enc
```

Deberías ver:

```bash
CV_EMAIL="name@company.com"
CV_PHONE="100 123 456"
```

Cuando esto funcione, borra el `.env` en claro:

```bash
rm .env
```

## 9. Editar secretos más adelante

Como tu fichero está en formato `dotenv`, usa siempre:

```bash
sops --input-type dotenv --output-type dotenv .env.enc
```

No uses simplemente:

```bash
sops .env.enc
```

porque SOPS intentará leerlo como JSON/YAML y dará error.

## 10. Plantilla de RenderCV

Tu plantilla debe usar variables:

`cv/Jesus_Erro_CV.template.yaml`

```yaml
cv:
  name: Your Name
  photo: ${CV_PHOTO}
  headline: Senior Backend Developer | Machine Learning | Data Analytics
  location: Pamplona, Navarra, España
  email: "${CV_EMAIL}"
  custom_connections:
    - placeholder: "${CV_PHONE}"
      url: "tel:${CV_PHONE}"
      fontawesome_icon: phone
```

### Nota sobre `phone`

RenderCV puede reformatear `cv.phone` automáticamente (`national`, `international`, `E164`).
Si quieres mostrar exactamente `600 000 111`, es mejor **no usar `phone:`** y usar `custom_connections` con:

- `placeholder`: lo que se ve
- `url`: el enlace `tel:...`

## 11. Crear `render.sh`

```bash
cat > render.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

set -a
source <(sops --decrypt --input-type dotenv --output-type dotenv .env.enc)
set +a

envsubst < cv/Your_Name_CV.template.yaml > cv/Your_Name.yaml
rendercv render cv/Your_Name_CV.yaml
EOF
```

Dar permisos:

```bash
chmod +x render.sh
```

## 12. Renderizar

```bash
./render.sh
```

Esto hace tres cosas:
1. Descifra `.env.enc`
2. Sustituye `${CV_EMAIL}`, `${CV_PHONE}`, etc. con `envsubst`
3. Ejecuta `rendercv render` sobre el YAML final

## 13. `.gitignore`

```gitignore
.env
cv/Jesus_Erro_CV.yaml
```

## 14. Comandos de uso diario

### Verificar herramientas
```bash
which age
which sops
which envsubst
sops --version
```

### Ver public key actual
```bash
grep '^# public key:' ~/.config/sops/age/keys.txt
```

### Editar secretos
```bash
sops --input-type dotenv --output-type dotenv .env.enc
```

### Descifrar y ver
```bash
sops --decrypt --input-type dotenv --output-type dotenv .env.enc
```

### Renderizar CV
```bash
./render.sh
```

## 15. Problemas típicos y solución

### Error: `no matching creation rules found`
Suele pasar porque:
- `.sops.yaml` no está en la raíz del proyecto
- `path_regex` no coincide
- falta `--filename-override .env.enc`

Solución:

```bash
sops encrypt \
  --filename-override .env.enc \
  --input-type dotenv \
  --output-type dotenv \
  .env > .env.enc
```

### Error: archivo `.env.enc` vacío
Suele pasar si interrumpes el comando (`Ctrl+Z`) después de que el shell haya creado el archivo de salida.

Solución:

```bash
rm -f .env.enc
sops encrypt \
  --filename-override .env.enc \
  --input-type dotenv \
  --output-type dotenv \
  .env > .env.enc
```

### Error: `invalid character 'C' looking for beginning of value`
Pasa al editar un `.env.enc` con:

```bash
sops .env.enc
```

Solución: indicar el formato `dotenv`:

```bash
sops --input-type dotenv --output-type dotenv .env.enc
```

### RenderCV no acepta `${CV_EMAIL}`
Eso es normal. RenderCV no interpola variables. Necesita el YAML final ya resuelto.

Solución:
- usar plantilla
- usar `envsubst`
- renderizar el archivo ya expandido

## 16. Flujo mínimo recomendado

```bash
# 1) Editar secretos
sops --input-type dotenv --output-type dotenv .env.enc

# 2) Renderizar
./render.sh
```

## 17. Resumen de la lógica

- La **public key** (`age1...`) puede estar en `.sops.yaml` y en Git.
- La **private key** (`AGE-SECRET-KEY-...`) se queda en `~/.config/sops/age/keys.txt`.
- El secreto real vive cifrado en `.env.enc`.
- RenderCV recibe solo el YAML final ya expandido.

## 18. Referencias útiles

- SOPS: https://github.com/getsops/sops
- age: https://github.com/FiloSottile/age
- RenderCV: https://docs.rendercv.com/
