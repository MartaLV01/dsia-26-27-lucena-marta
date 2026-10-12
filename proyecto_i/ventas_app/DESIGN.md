SRP (Single Responsibility Principle) — validator.py, clase SalesValidator: se encarga de validar los datos y separar los registros válidos de los inválidos. La carga de archivos y el cálculo de métricas están en módulos distintos.

DIP (Dependency Inversion Principle) — loader.py, SalesRepository: define un contrato mediante Protocol. cli.py utiliza ese contrato en lugar de depender directamente del tipo concreto de repositorio en la anotación de la variable.

OCP (Open/Closed Principle) — metrics.py, clase SalesMetrics: las métricas se encuentran separadas del validador. Se pueden añadir nuevos cálculos ampliando el módulo de métricas sin modificar la lógica de validación.