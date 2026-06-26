from pdf_engine import build_pdf

content = {
    "title": "Informe T\u00e9cnico",
    "subtitle": "Sistema Centralizado de Gesti\u00f3n de Activos IT \u2014 Inventario ITU",
    "output": "informe-inventario-itu.pdf",
    "show_toc": True,
    "theme": {
        "primary": "#0D3B66",
        "accent":  "#E94560",
        "light":   "#F5F5F5",
        "text":    "#2D2D2D",
        "muted":   "#888888",
    },
    "meta": {
        "autor": "Instituto Tecnol\u00f3gico Universitario \u2014 Universidad Nacional de Cuyo",
        "fecha": "Junio 2026",
        "versi\u00f3n": "1.0",
        "asignaturas": "Sistemas Operativos Aplicados: Linux \u00b7 Windows \u00b7 Computaci\u00f3n en la Nube \u00b7 Bases de Datos Avanzadas",
        "autores": "C\u00e9sar Mar\u00edn \u00b7 Maximiliano Lopez \u00b7 Franco Rossi \u00b7 Micaela Becerra",
    },
    "sections": [
        {
            "heading": "Resumen",
            "body": "El presente informe documenta el dise\u00f1o, implementaci\u00f3n y despliegue del sistema <i>Inventario ITU</i>, desarrollado como proyecto integrador de cuatro asignaturas del Instituto Tecnol\u00f3gico Universitario (ITU), dependiente de la Universidad Nacional de Cuyo. El sistema centraliza la gesti\u00f3n del inventario inform\u00e1tico de los laboratorios de la instituci\u00f3n mediante una arquitectura de m\u00faltiples capas que integra bases de datos heterog\u00e9neas (SQL Server y MongoDB), autenticaci\u00f3n corporativa mediante Active Directory y LDAP, contenerizaci\u00f3n con Docker, orquestaci\u00f3n con Kubernetes (Minikube) y pol\u00edticas de red de tipo <i>zero-trust</i>. El proyecto fue desarrollado de forma colaborativa con control de versiones Git, validado sobre m\u00faltiples plataformas (Linux Mint, Ubuntu Server, Lubuntu y macOS Tahoe) y cuenta con un pipeline de integraci\u00f3n y despliegue continuo (CI/CD) automatizado mediante GitHub Actions.",
        },
        {
            "heading": "1. Introducci\u00f3n",
            "body": "Las instituciones educativas que disponen de m\u00faltiples laboratorios de inform\u00e1tica enfrentan un desaf\u00edo estructural: mantener un registro actualizado, confiable y accesible de la totalidad de sus activos tecnol\u00f3gicos. En ausencia de un sistema centralizado, el personal t\u00e9cnico se ve obligado a gestionar inventarios de forma manual o dispersa en hojas de c\u00e1lculo, incrementando el riesgo de errores, duplicaci\u00f3n de informaci\u00f3n, p\u00e9rdida de datos y dificultades para planificar mantenimientos preventivos.<br/><br/>El presente proyecto da respuesta a esta problem\u00e1tica mediante el desarrollo de una aplicaci\u00f3n web institucional que permite consultar, registrar y actualizar los equipos de los laboratorios del ITU. Cada m\u00e1quina queda caracterizada por dos dimensiones complementarias: su informaci\u00f3n de ubicaci\u00f3n y asignaci\u00f3n (laboratorio, banco, responsable, estado, fecha de mantenimiento), almacenada en una base de datos relacional SQL Server; y sus especificaciones de hardware (CPU, RAM, disco, sistema operativo, perif\u00e9ricos), almacenadas en una base de datos documental MongoDB. El acceso al sistema est\u00e1 controlado \u00edntegramente por los grupos y credenciales del Active Directory institucional, de modo que cada usuario opera \u00fanicamente con los permisos correspondientes a su rol.<br/><br/>El proyecto fue concebido desde su inicio como un ecosistema de producci\u00f3n real: se ejecuta contenerizado en Kubernetes, se despliega autom\u00e1ticamente ante cada push a la rama principal mediante un runner self-hosted, y est\u00e1 protegido por un firewall pfSense que act\u00faa como \u00fanico punto de entrada autorizado desde la red del aula.",
        },
        {
            "heading": "2. Objetivos",
            "body": "Objetivo general: Dise\u00f1ar, implementar y desplegar un sistema centralizado de gesti\u00f3n de activos IT para los laboratorios del ITU, con arquitectura contenerizada, autenticaci\u00f3n institucional y pol\u00edticas de seguridad de red.",
            "bullets": [
                "Dise\u00f1ar un modelo de datos h\u00edbrido que combine SQL Server y MongoDB para representar distintos aspectos del inventario, justificando la elecci\u00f3n de cada motor seg\u00fan la naturaleza de la informaci\u00f3n.",
                "Integrar autenticaci\u00f3n y autorizaci\u00f3n con el Active Directory institucional mediante el protocolo LDAP.",
                "Implementar control de acceso basado en roles (RBAC) con cuatro niveles diferenciados derivados de los grupos de AD.",
                "Desplegar el sistema en un cl\u00faster Kubernetes (Minikube) con CNI Calico, pol\u00edticas de red <i>default-deny</i> y reglas de egress expl\u00edcitas.",
                "Configurar el acceso externo seguro a trav\u00e9s de pfSense mediante reenv\u00edo de puertos y reglas NAT hacia el cl\u00faster.",
                "Automatizar el ciclo de integraci\u00f3n y despliegue continuo (CI/CD) mediante GitHub Actions con un runner self-hosted en la VM de producci\u00f3n.",
                "Desarrollar y mantener el proyecto \u00edntegramente bajo control de versiones Git, con convenciones de commits, ramas y flujo de integraci\u00f3n documentados.",
                "Validar el sistema sobre m\u00faltiples plataformas: Linux Mint, Ubuntu Server, Lubuntu y macOS Tahoe.",
            ],
        },
        {
            "heading": "3. Metodolog\u00eda de Trabajo y Control de Versiones",
            "table": {
                "headers": ["Rama", "Prop\u00f3sito"],
                "rows": [
                    ["main", "Producci\u00f3n \u2014 siempre estable, disparador del pipeline CD"],
                    ["develop", "Integraci\u00f3n \u2014 base para nuevas features"],
                    ["feature/&lt;nombre&gt;", "Nueva funcionalidad"],
                    ["fix/&lt;nombre&gt;", "Correcci\u00f3n de bug"],
                    ["hotfix/&lt;nombre&gt;", "Correcci\u00f3n urgente directa sobre main"],
                ],
                "col_widths": [4.0, 13.0],
            },
            "note": "El flujo normal de integraci\u00f3n fue feature/* \u2192 develop \u2192 main. Los hotfixes se aplicaron sobre main y luego se mergearon de vuelta a develop para mantener la coherencia.",
        },
        {
            "heading": "3.1 Organizaci\u00f3n del equipo",
            "body": "El proyecto fue desarrollado por un equipo de cuatro integrantes que dividieron el trabajo por dominios t\u00e9cnicos: infraestructura y Kubernetes, backend y base de datos relacional, autenticaci\u00f3n AD/LDAP, y frontend. La integraci\u00f3n de las contribuciones individuales se realiz\u00f3 \u00edntegramente a trav\u00e9s de un repositorio Git unificado, permitiendo que el tribunal pudiera verificar la evoluci\u00f3n del c\u00f3digo, la autor\u00eda de cada cambio y la progresi\u00f3n del sistema a lo largo del tiempo.",
        },
        {
            "heading": "3.2 Estrategia de branching",
            "body": "Se adopt\u00f3 un flujo de trabajo estructurado con las siguientes ramas:",
        },
        {
            "heading": "3.3 Convenci\u00f3n de commits",
            "body": "Se adopt\u00f3 el est\u00e1ndar <a href=\"https://www.conventionalcommits.org/\">Conventional Commits</a> con la estructura &lt;tipo&gt;(&lt;scope&gt;): &lt;descripci\u00f3n&gt;. Los tipos utilizados fueron feat, fix, docs, chore, refactor, test y ci, con scopes definidos por capa: frontend, backend, k8s, db, auth, docs. Esto permiti\u00f3 generar un historial de cambios sem\u00e1nticamente legible y facilitar la revisi\u00f3n durante la defensa del proyecto.",
        },
        {
            "heading": "3.4 Validaci\u00f3n multiplataforma",
            "body": "El sistema fue probado sobre las siguientes plataformas durante el desarrollo y la preparaci\u00f3n de la defensa:",
            "table": {
                "headers": ["Plataforma", "Rol en las pruebas"],
                "rows": [
                    ["Lubuntu", "VM de producci\u00f3n y entrega final \u2014 Minikube, GitHub Actions Runner, iptables"],
                    ["Ubuntu Server", "Validaci\u00f3n de build de im\u00e1genes Docker durante el desarrollo"],
                    ["Linux Mint", "Estaciones de desarrollo del equipo"],
                    ["macOS Tahoe", "Desarrollo local \u2014 modo mock y Docker Compose; kubectl port-forward para acceso al cl\u00faster"],
                ],
                "col_widths": [4.0, 13.0],
            },
            "note": "En macOS, la ausencia de iptables requiri\u00f3 el uso de kubectl port-forward --address=0.0.0.0 para exponer el frontend a la red local, dado que Minikube con driver Docker a\u00edsla el cl\u00faster en una subred interna no enrutable desde el host.",
        },
        {
            "heading": "4. Arquitectura del Sistema",
            "highlight": "El sistema sigue una arquitectura en capas inspirada en el modelo de Spring Boot, con inyecci\u00f3n de dependencias manual. Cada capa conoce \u00fanicamente a la inmediata inferior, garantizando bajo acoplamiento y la posibilidad de sustituir implementaciones sin impactar las capas superiores.",
        },
        {
            "heading": "4.1 Visi\u00f3n general",
            "body": "El sistema sigue una arquitectura en tres capas: frontend SPA, backend API REST, y almacenamiento heterog\u00e9neo.",
            "code": "Frontend (React SPA)\n       \u2193  HTTP\nBackend (Node.js / Express 5)\n   \u251c\u2500\u2500 SQL Server  (ubicaci\u00f3n y asignaci\u00f3n de m\u00e1quinas)\n   \u251c\u2500\u2500 MongoDB     (especificaciones de hardware)\n   \u2514\u2500\u2500 LDAP / AD   (autenticaci\u00f3n y usuarios)",
            "language": "text",
        },
        {
            "heading": "4.2 Stack tecnol\u00f3gico",
            "table": {
                "headers": ["Capa", "Tecnolog\u00eda"],
                "rows": [
                    ["Frontend", "React 19 + TypeScript + Vite + React Router"],
                    ["Backend", "Node.js + Express 5 + TypeScript"],
                    ["Base de datos relacional", "SQL Server (VM dedicada, 192.168.1.20:1433)"],
                    ["Base de datos documental", "MongoDB 4.4 (in-cluster)"],
                    ["Autenticaci\u00f3n", "Active Directory / LDAP (192.168.1.10:389)"],
                    ["Contenerizaci\u00f3n", "Docker + Docker Compose"],
                    ["Orquestaci\u00f3n", "Kubernetes (Minikube con CNI Calico)"],
                    ["CI/CD", "GitHub Actions (runner self-hosted)"],
                    ["Firewall perimetral", "pfSense"],
                ],
                "col_widths": [7.0, 10.0],
            },
        },
        {
            "heading": "4.3 Estructura del backend",
            "body": "El backend organiza el c\u00f3digo en capas con responsabilidades claramente delimitadas:",
            "code": "src/\n\u251c\u2500\u2500 app.ts          # Setup Express, middlewares, montaje de rutas\n\u251c\u2500\u2500 server.ts       # Entry point\n\u251c\u2500\u2500 config.ts       # Variables de entorno tipadas\n\u251c\u2500\u2500 routes/         # Definici\u00f3n de endpoints + middlewares\n\u251c\u2500\u2500 controllers/    # Manejo de request/response\n\u251c\u2500\u2500 services/       # L\u00f3gica de negocio\n\u251c\u2500\u2500 repositories/\n\u2502   \u251c\u2500\u2500 interfaces/ # Contratos de repositorio\n\u2502   \u251c\u2500\u2500 sql/        # Implementaci\u00f3n SQL Server\n\u2502   \u251c\u2500\u2500 mongo/      # Implementaci\u00f3n MongoDB\n\u2502   \u2514\u2500\u2500 ldap/       # Implementaci\u00f3n Active Directory\n\u251c\u2500\u2500 mock/repositories/ # Implementaciones en memoria (dev/test)\n\u251c\u2500\u2500 middleware/     # Auth JWT + RBAC\n\u2514\u2500\u2500 lib/            # Permisos + errores custom",
            "language": "bash",
            "note": "Cada interfaz de repositorio tiene dos implementaciones: una <b>real</b> y una <b>mock</b>. El switch se controla con la variable MOCK_MODE.",
        },
        {
            "heading": "4.4 Topolog\u00eda de red",
            "body": "El entorno de producci\u00f3n consiste en cuatro m\u00e1quinas virtuales ejecut\u00e1ndose sobre VirtualBox en una PC con Windows, conectadas a la red interna 192.168.1.0/24 administrada por pfSense.",
            "table": {
                "headers": ["Host", "IP", "Rol"],
                "rows": [
                    ["pfSense LAN", "192.168.1.254", "Gateway interno y punto de entrada desde el aula"],
                    ["VM Linux (Lubuntu)", "192.168.1.50", "Minikube + GitHub Actions Runner"],
                    ["VM SQL Server", "192.168.1.20", "Base de datos relacional (ITUSRV002, instancia ITULAB)"],
                    ["VM Active Directory", "192.168.1.10", "Autenticaci\u00f3n LDAP (OU=EGI,DC=itu,DC=local)"],
                ],
                "col_widths": [5.0, 3.5, 8.5],
            },
            "note": "Las reglas iptables se persisten en /etc/iptables/rules.v4 y se restauran autom\u00e1ticamente al arrancar mediante un servicio systemd (iptables-restore.service), garantizando que el sistema est\u00e9 disponible tras cada reinicio de la VM sin intervenci\u00f3n manual.",
        },
        {
            "heading": "5. Modelo de Datos",
            "body": "El dise\u00f1o de datos refleja la naturaleza dual de la informaci\u00f3n gestionada. SQL Server es la opci\u00f3n adecuada para los datos de ubicaci\u00f3n y asignaci\u00f3n porque son altamente estructurados, con campos fijos y relaciones definidas. MongoDB, en cambio, es apropiado para el hardware porque las especificaciones de los equipos son heterog\u00e9neas y el modelo documental permite actualizaciones parciales sin necesidad de migrar esquemas.",
        },
        {
            "heading": "5.1 SQL Server \u2014 tabla machines",
            "table": {
                "headers": ["Columna", "Tipo", "Descripci\u00f3n"],
                "rows": [
                    ["id", "INT IDENTITY", "Clave primaria autoincremental"],
                    ["hostname", "VARCHAR(100)", "Nombre de red del equipo (ej. lab101-pc01)"],
                    ["lab", "VARCHAR(50)", "Laboratorio al que pertenece"],
                    ["bench_number", "INT", "N\u00famero de banco o mesa"],
                    ["maintenance_date", "DATE", "Fecha del \u00faltimo mantenimiento"],
                    ["status", "VARCHAR(20)", "active, maintenance o retired"],
                    ["assignee", "VARCHAR(100)", "Nombre del responsable asignado"],
                    ["assignee_type", "VARCHAR(20)", "student, teacher o technician"],
                ],
                "col_widths": [4.0, 3.5, 9.5],
            },
        },
        {
            "heading": "5.2 MongoDB \u2014 colecci\u00f3n hardware",
            "table": {
                "headers": ["Campo", "Tipo", "Descripci\u00f3n"],
                "rows": [
                    ["machineId", "number", "Referencia a machines.id"],
                    ["type", "string", "desktop o laptop"],
                    ["manufacturer / model", "string", "Fabricante y modelo"],
                    ["cpu", "string", "Procesador"],
                    ["ramGb / diskGb", "number", "RAM y almacenamiento en GB"],
                    ["os", "string", "Sistema operativo instalado"],
                    ["monitor / mouse / keyboard", "string", "Perif\u00e9ricos"],
                ],
                "col_widths": [5.5, 2.0, 9.5],
            },
            "note": "La relaci\u00f3n entre ambas colecciones es 1 a 1 mediante machineId. El Job de seed de MongoDB es idempotente: verifica si la colecci\u00f3n ya contiene documentos antes de insertar.",
        },
        {
            "heading": "5.3 Active Directory",
            "body": "Los usuarios no residen en ninguna de las dos bases de datos propias del sistema. Viven \u00edntegramente en el Active Directory institucional bajo OU=EGI,DC=itu,DC=local. El backend consulta el AD para autenticar credenciales y recuperar los grupos de pertenencia de cada usuario, que luego se mapean a los roles del sistema.",
        },
        {
            "heading": "6. Autenticaci\u00f3n y Control de Acceso",
            "body": "",
        },
        {
            "heading": "6.1 Flujo de autenticaci\u00f3n",
            "body": "El proceso de autenticaci\u00f3n integra el frontend, el backend y el Active Directory en una cadena sin estado basada en JWT. El usuario ingresa sus credenciales, el backend realiza un bind LDAP contra el AD, los grupos se mapean a roles, se firma un JWT y cada solicitud posterior incluye el token en el header Authorization: Bearer &lt;token&gt;. Si el token expira o el backend responde 401, el frontend redirige al login autom\u00e1ticamente.",
        },
        {
            "heading": "6.2 Roles y permisos (RBAC)",
            "table": {
                "headers": ["Rol", "Grupos AD", "Permisos"],
                "rows": [
                    ["sysadmin", "GRP_Sysadmin", "CRUD completo en m\u00e1quinas, hardware y usuarios"],
                    ["manager", "GRP_Manager", "CRUD en m\u00e1quinas y hardware; lectura de usuarios"],
                    ["technician", "GRP_Technician", "Lectura y actualizaci\u00f3n de m\u00e1quinas y hardware"],
                    ["teacher", "GRP_Teacher", "Solo lectura del inventario"],
                ],
                "col_widths": [3.0, 4.0, 10.0],
            },
            "note": "El RBAC se implementa mediante dos middlewares encadenados: auth.middleware.ts verifica el JWT, rbac.middleware.ts comprueba que el rol tenga el permiso requerido.",
        },
        {
            "heading": "7. Seguridad",
            "body": "La seguridad fue tratada como una dimensi\u00f3n transversal del proyecto, no como un a\u00f1adido posterior. El equipo mantuvo una hoja de ruta documentada en docs/seguridad.md con \u00edtems numerados, clasificados por criticidad y con estado de resoluci\u00f3n expl\u00edcito.",
            "bullets": [
                "<b>Inyecci\u00f3n LDAP:</b> Los filtros de b\u00fasqueda escapan los valores del usuario antes de construir las expresiones LDAP.",
                "<b>Inyecci\u00f3n SQL:</b> Todas las consultas a SQL Server utilizan par\u00e1metros tipados mediante sql.input() del driver mssql.",
                "<b>Headers de seguridad HTTP:</b> El middleware helmet aplica cabeceras de protecci\u00f3n en todas las respuestas del backend (HSTS, X-Frame-Options, CSP).",
                "<b>CORS restringido:</b> Los or\u00edgenes permitidos se controlan mediante la variable de entorno CORS_ORIGINS.",
                "<b>JWT seguro:</b> El secreto JWT se obtiene exclusivamente de variable de entorno. Los tokens incluyen los claims iss y aud.",
                "<b>Validaci\u00f3n y sanitizaci\u00f3n:</b> Toda la entrada de usuario se valida con schemas Zod y se sanitiza contra XSS.",
                "<b>Network Policies \u2014 Zero-Trust:</b> El namespace opera con una pol\u00edtica deny-all por defecto (Calico).",
                "<b>MongoDB autenticada:</b> Acceso requiere usuario y contrase\u00f1a (egi_user).",
                "<b>Integraci\u00f3n AD \u2192 SQL Server:</b> Logins sincronizados con grupos de AD mediante ad-sqlserver-logins.sql.",
                "<b>Logging de intentos fallidos:</b> El backend registra intentos de autenticaci\u00f3n fallidos con timestamp y usuario.",
                "<b>Persistencia de reglas iptables:</b> Reglas guardadas en /etc/iptables/rules.v4 y restauradas autom\u00e1ticamente al arrancar.",
            ],
        },
        {
            "heading": "8. API REST",
            "table": {
                "headers": ["M\u00e9todo", "Ruta", "Descripci\u00f3n"],
                "rows": [
                    ["POST", "/api/auth/login", "Autenticaci\u00f3n contra AD/LDAP, devuelve JWT"],
                    ["GET", "/api/machines", "Listar todas las m\u00e1quinas (requiere machines:list)"],
                    ["POST", "/api/machines", "Crear m\u00e1quina (requiere machines:create)"],
                    ["PUT", "/api/machines/:id", "Actualizar m\u00e1quina (requiere machines:update)"],
                    ["DELETE", "/api/machines/:id", "Eliminar m\u00e1quina y su hardware (requiere machines:delete)"],
                    ["GET", "/api/machines/:id/hardware", "Hardware de una m\u00e1quina"],
                    ["PUT", "/api/machines/:id/hardware", "Actualizar hardware (upsert en MongoDB)"],
                    ["GET", "/api/users", "Listar usuarios AD (requiere users:list)"],
                    ["POST", "/api/users", "Crear usuario en AD"],
                    ["PUT", "/api/users/:id", "Modificar usuario y sus grupos en AD"],
                    ["DELETE", "/api/users/:id", "Eliminar usuario de AD"],
                    ["GET", "/health", "Estado del servicio y modo de operaci\u00f3n"],
                ],
                "col_widths": [2.5, 5.5, 9.0],
            },
            "note": "La eliminaci\u00f3n de una m\u00e1quina ejecuta una operaci\u00f3n en dos pasos: primero elimina el documento de hardware en MongoDB, luego elimina el registro en SQL Server.",
        },
        {
            "heading": "9. Despliegue y CI/CD",
            "body": "",
        },
        {
            "heading": "9.1 Infraestructura Kubernetes",
            "body": "El despliegue en producci\u00f3n se organiza en el namespace inventario-itu con recursos declarativos: Deployments para frontend (nginx:1.27), backend (Node.js) y MongoDB (4.4); Services NodePort 30080 para frontend y ClusterIP para backend y MongoDB; PersistentVolumeClaim de 1 Gi para MongoDB; ConfigMap + Job idempotente para carga inicial de datos; Secret con variables de entorno del backend; NetworkPolicies con deny-all m\u00e1s seis reglas expl\u00edcitas.",
            "table": {
                "headers": ["Fase", "Script", "Qu\u00e9 hace"],
                "rows": [
                    ["Core", "k8s/deploy-core.sh", "Namespace \u2192 MongoDB \u2192 Backend \u2192 Frontend \u2192 Network Policies \u2192 iptables \u2192 smoke test"],
                    ["Seed", "k8s/seed-data.sh", "Bootstrap SQL Server + Job idempotente MongoDB"],
                ],
                "col_widths": [2.5, 5.0, 9.5],
            },
        },
        {
            "heading": "9.2 Pipeline CI/CD",
            "body": "CI (ci.yml): se ejecuta en cada Pull Request a main o develop usando runners hospedados en GitHub. Realiza lint, verificaci\u00f3n de tipos con TypeScript y build de ambas aplicaciones. CD (deploy.yml): se ejecuta en cada push a main mediante un runner self-hosted en la VM Linux de producci\u00f3n. El flujo completo es:",
            "code": "bootstrap SQL \u2192 build im\u00e1genes Docker \u2192 push a GHCR\n     \u2192 kubectl apply \u2192 rollout status \u2192 iptables (safety net) \u2192 smoke test",
            "language": "text",
            "note": "El smoke test final verifica que el endpoint /health del backend responda con status ok y mockMode=false, confirmando que el despliegue es funcional de extremo a extremo.",
        },
        {
            "heading": "10. Testing",
            "body": "",
        },
        {
            "heading": "10.1 Tests automatizados",
            "body": "El backend cuenta con una suite de tests unitarios ejecutada con Jest, organizada en backend/src/__tests__/. Los tests cubren las implementaciones de repositorios mock y la l\u00f3gica de permisos RBAC.",
            "code": "cd backend\nnpm test           # ejecuci\u00f3n \u00fanica\nnpm run test:watch # modo watch durante desarrollo",
            "language": "bash",
        },
        {
            "heading": "10.2 Validaci\u00f3n multiplataforma",
            "body": "El equipo realiz\u00f3 pruebas en Lubuntu (producci\u00f3n), Ubuntu Server (build de im\u00e1genes Docker), Linux Mint (estaciones de desarrollo) y macOS Tahoe (desarrollo local con modo mock y Docker Compose con Azure SQL Edge para Apple Silicon).",
        },
        {
            "heading": "11. Modos de Operaci\u00f3n",
            "table": {
                "headers": ["Modo", "Descripci\u00f3n", "Requisitos"],
                "rows": [
                    ["Mock", "Datos y autenticaci\u00f3n completamente en memoria. Sin conexiones externas.", "Solo Node.js 20+ instalado."],
                    ["Real con Docker", "SQL Server + MongoDB v\u00eda Docker Compose. LDAP sigue siendo mock.", "Docker instalado."],
                    ["Producci\u00f3n (Minikube)", "Despliegue completo con AD, SQL Server y MongoDB reales.", "Minikube + acceso a la LAN del laboratorio."],
                ],
                "col_widths": [5.0, 7.0, 5.0],
            },
            "note": "El modo se controla de forma independiente en backend (MOCK_MODE) y frontend (VITE_USE_MOCK). Ambas variables deben estar coordinadas.",
        },
        {
            "heading": "12. Conclusiones",
            "body": "El proyecto <i>Inventario ITU</i> alcanz\u00f3 la totalidad de los objetivos planteados en la consigna: un sistema real, funcional y desplegado, no una demostraci\u00f3n acad\u00e9mica simulada.<br/><br/>Desde el punto de vista de la ingenier\u00eda de software, la separaci\u00f3n entre interfaces de repositorio e implementaciones concretas demostr\u00f3 ser la decisi\u00f3n de dise\u00f1o m\u00e1s valiosa del proyecto. Permiti\u00f3 desarrollar y testear toda la l\u00f3gica de negocio en modo mock sin infraestructura externa, y luego conectar las bases de datos reales sin tocar ninguna capa superior.<br/><br/>La integraci\u00f3n de cuatro asignaturas en un \u00fanico proyecto cohesivo \u2014Linux, Windows, Computaci\u00f3n en la Nube y Bases de Datos Avanzadas\u2014 exigi\u00f3 al equipo razonar simult\u00e1neamente sobre administraci\u00f3n de sistemas operativos, seguridad de red, orquestaci\u00f3n de contenedores y modelado de datos. El resultado es un sistema que no solo funciona, sino que est\u00e1 documentado, versionado, automatizado y validado sobre m\u00faltiples plataformas.<br/><br/>Las mejoras identificadas (TLS extremo a extremo, LDAP sobre TLS, rate limiting en el endpoint de login, gesti\u00f3n de secretos con SealedSecrets y validaci\u00f3n server-side con Zod) constituyen una hoja de ruta clara para un eventual endurecimiento del sistema antes de un despliegue institucional permanente.",
        },
        {
            "heading": "Referencias",
            "bullets": [
                "Documentaci\u00f3n oficial de Kubernetes: Network Policies. &lt;https://kubernetes.io/docs/concepts/services-networking/network-policies/&gt;",
                "OWASP Foundation: LDAP Injection Prevention Cheat Sheet. &lt;https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html&gt;",
                "OWASP Foundation: JWT Security Cheat Sheet. &lt;https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html&gt;",
                "Microsoft: SQL Server T-SQL Reference. &lt;https://learn.microsoft.com/en-us/sql/t-sql/language-reference&gt;",
                "MongoDB: Data Modeling Introduction. &lt;https://www.mongodb.com/docs/manual/core/data-modeling-introduction/&gt;",
                "Conventional Commits: A specification for adding human and machine readable meaning to commit messages. &lt;https://www.conventionalcommits.org/&gt;",
                "Tigera: Calico Network Policy. &lt;https://docs.tigera.io/calico/latest/network-policy/&gt;",
                "Zod: TypeScript-first schema validation with static type inference. &lt;https://zod.dev/&gt;",
                "Repositorio del proyecto: &lt;https://github.com/CesarMarinMorla/egi&gt;",
            ],
        },
    ],
}

path = build_pdf(content)
print(f"PDF generado en: {path}")
