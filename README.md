# Odoo Mobile Client

Instancia Odoo 19 gestionada con [saas-platform-cli](https://github.com/pachedev/saas-platform-cli).

| | |
|---|---|
| **Proyecto** | `odoo-mobile-client` |
| **Entorno** | `prod` |
| **Odoo** | v19 |
| **Contenedor** | `odoo-mobile-client-odoo19` |
| **Base de datos** | `omc_v19_prod` |
| **PostgreSQL** | runtime compartido (`postgres-runtime:1920`) |
| **Puerto HTTP** | `8101` |
| **Puerto chat** | `8201` (`gevent_port`) |
| **Red Docker** | `proxy` |
| **Idioma** | `es_MX` |
| **Datos demo** | no |

---

## Estructura

```
odoo-mobile-client/
├── docker-compose.yml    ← servicios de la instancia (rutas del host desde el .env)
├── .env                  ← secretos y rutas de ESTA máquina — NO se versiona
├── .env.example          ← plantilla documentada de las variables
├── entrypoint.sh         ← inyecta credenciales en runtime, instala requirements
├── addons/               ← módulos personalizados o de terceros
├── etc/
│   ├── odoo.conf         ← configuración de Odoo
│   └── requirements.txt  ← dependencias Python extra
└── logs/                 ← odoo-server.log (montado en /var/log/odoo)
```

---

## Puesta en marcha en una máquina nueva

El `.env` no está en el repositorio: contiene secretos y las rutas de datos propias de
cada host. Después de clonar:

```bash
export PLATFORM_ROOT=/opt/platform        # el que aplique en este host

render-odoo-env --project odoo-mobile-client --env prod
odoo-service --project odoo-mobile-client --env prod --action start
```

`render-odoo-env` reconstruye el `.env` resolviendo las rutas contra el `PLATFORM_ROOT`
local. Los valores no secretos (puertos, nombre de DB, idioma) los recupera de
`etc/odoo.conf` y `docker-compose.yml`. Usa `--print` para ver el resultado sin escribirlo.

Requisitos previos en el host: plataforma inicializada (`init-platform`), red Docker
`proxy` creada y `postgres-runtime` en marcha.

---

## Rutas de datos

Las rutas **dentro** del contenedor son fijas. Lo configurable es la ruta del **host**,
definida en el `.env`:

| Dentro del contenedor (fijo) | Ruta del host (`.env`) |
|---|---|
| `/var/lib/odoo/filestore` | `HOST_FILESTORE_PATH` |
| `/var/lib/odoo/sessions` | `HOST_SESSIONS_PATH` |

Por defecto apuntan a `$PLATFORM_ROOT/shared/{filestore,sessions}/prod/odoo-mobile-client`.
Pueden apuntar a otro disco sin tocar el `docker-compose.yml`.

> Cambiar un `HOST_*_PATH` **no mueve datos**. Odoo arrancaría contra un directorio vacío
> y los adjuntos dejarían de resolverse. Para mover el filestore: detén la instancia,
> copia el directorio, actualiza el `.env`, levanta.

La base de datos `omc_v19_prod` vive en `postgres-runtime`, fuera de este proyecto.

---

## Operación

```bash
# Servicio
odoo-service --project odoo-mobile-client --env prod --action start|stop|restart|status

# Logs
odoo-service --project odoo-mobile-client --env prod --action logs          # log de Odoo
odoo-service --project odoo-mobile-client --env prod --action logs-docker   # log del contenedor

# Actualizar módulos
odoo-service --project odoo-mobile-client --env prod --action update --module <modulo>
odoo-service --project odoo-mobile-client --env prod --action update-all

# Backup / restauración
backup-odoo  --project odoo-mobile-client --env prod
restore-odoo --project odoo-mobile-client --env prod --dump <archivo.sql> --stop
```

`update` y `update-all` corren Odoo con `--stop-after-init`; el script reinicia el
contenedor al terminar.

---

## Addons personalizados

Se colocan en `addons/`, montado como `/mnt/extra-addons`. Tras agregar o modificar
un módulo:

```bash
odoo-service --project odoo-mobile-client --env prod --action update --module <modulo>
```

Dependencias Python extra: agrégalas a `etc/requirements.txt` — `entrypoint.sh` las
instala en cada arranque del contenedor.

---

## Nginx Proxy Manager

| Campo | Valor |
|---|---|
| Esquema | `http` |
| Host de reenvío | `odoo-mobile-client-odoo19` |
| Puerto | `8101` |
| Websockets | activado |
| Forzar SSL / HTTP/2 | activado |

Ubicación personalizada para el chat:

```nginx
location /websocket {
    proxy_pass http://odoo-mobile-client-odoo19:8201/websocket;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

El acceso externo pasa por NPM a través de la red Docker `proxy`. El compose de servidor
no publica puertos al host; el modo lab (`--lab`) sí los expone para pruebas locales.

> Si eliminas esta instancia, borra o deshabilita primero su proxy host en NPM. Un host
> apuntando a un contenedor inexistente impide que nginx arranque y tumba **todos** los
> sitios.

---

## Advertencias

- `.env` contiene la contraseña de la base de datos y la master password de Odoo. Nunca
  se sube al repositorio (ya está en `.gitignore`).
- `list_db = False` y `dbfilter` restringen la instancia a su propia base de datos.
- `proxy_mode = True` es obligatorio: la instancia siempre corre detrás de NPM.
