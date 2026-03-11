# Contexto del Proyecto: Gestion Visual de Proyectos

## 1. Descripción del Proyecto

Este proyecto es una aplicación de gestión de tareas inspirada en la metodología **Kanban**, diseñada para ayudar a equipos e individuos a visualizar su flujo de trabajo. Al igual que Trello, permite organizar ideas, tareas y proyectos en tableros dinámicos, ofreciendo una experiencia de usuario fluida e intuitiva.

## 2. Stack Tecnológico

### FRONTEND

- **Entorno de Desarrollo:** pnpm.
- **Lenguaje:** TypeScript (Strict mode).
- **Framework:** Next.js.
- **Estilos:** TailwindCSS.
- **Componentes UI:** Shadcn UI.
- **Auth:** AuthJS.
- **Validaciones:** Zod + React Hook Form.
  
```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

// 1. Defines el esquema de "la verdad"
const userSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
});

// 2. Extraes el tipo automáticamente
type UserForm = z.infer<typeof userSchema>;

export default function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<UserForm>({
    resolver: zodResolver(userSchema), // 3. La conexión mágica
  });

  const onSubmit = (data: UserForm) => console.log(data);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email")} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register("password")} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Enviar</button>
    </form>
  );
}
```

- **Versionado:** Git.
- **Control de Versiones:** GitHub.

## 3. Reglas de Codificación

### General

- Usa el idioma ingles
- Prefiere la programación funcional y componentes limpios.
- Documenta las funciones complejas en español.
- No uses variables globales.
- Utiliza versiones para las rutas de la API.

### Frontend & UI (Tailwind + Shadcn)

- Usa **TypeScript** estricto para todo. Define interfaces o tipos para todas las estructuras de datos, especialmente las que vienen de la base de datos.
- Usa pnpm para instalar dependencias.
- **Estilos:** No escribas CSS personalizado. Usa siempre las clases utilitarias de **TailwindCSS**.
- **Componentes:** Para botones, inputs, modales y tablas, utiliza siempre los componentes de **Shadcn**. No crees componentes HTML nativos si existe una alternativa en Shadcn.
- **Diseño:** La interfaz debe ser limpia y responder a dispositivos móviles (Mobile-first).

## 4. Convenciones de Nombres

- **Base de Datos:** `camelCase` para campos (ej: `beginDate`), `PascalCase` para modelos (ej: `Ticket`, `Task`).
- **Variables:** `camelCase` (ej: `espaciosDisponibles`).
- **Archivos:** `kebab-case` o seguir la convención del framework.

## 6. 🚀 Características Principales

- Tableros Dinámicos: Crea múltiples espacios de trabajo para diferentes proyectos.
- Gestion de usuarios y roles.
- Sistema de Listas y Tarjetas: Organiza tus tareas en columnas personalizables (Ej: Por hacer, En progreso, Finalizado).
- Drag & Drop (Arrastrar y Soltar): Interfaz interactiva para mover tarjetas entre listas de forma sencilla.
- Gestión Detallada de Tareas: Añade descripciones, etiquetas de colores, fechas de vencimiento, notas, archivos y checklists a cada tarjeta.
- Historial de interacciones.
- Persistencia de Datos: Sincronización en tiempo real para que nunca pierdas tus avances.
