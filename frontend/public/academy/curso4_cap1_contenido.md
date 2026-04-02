# Capítulo 1: ¿Qué es un pedimento y cómo leerlo?
### Curso: Importaciones y Comercio Exterior — MYSTIC Academy

---

## Introducción

Si alguna vez has importado mercancía para tu empresa —o si estás pensando hacerlo— habrás escuchado la palabra "pedimento". Este documento es el corazón del proceso aduanal en México: sin él, ninguna mercancía puede entrar ni salir legalmente del país.

El pedimento es largo, técnico y lleno de claves y códigos que parecen diseñados para confundir. Sin embargo, una vez que entiendes su estructura, puedes leerlo en minutos y detectar errores que podrían costarte caro: desde pagar más impuestos de los necesarios hasta tener tu mercancía retenida en la aduana.

En este capítulo aprenderás qué es un pedimento, para qué sirve cada sección, cuáles son los tipos más comunes y cómo identificar los impuestos que estás pagando.

---

## 1. ¿Qué es un pedimento aduanal?

El pedimento es el **documento oficial que ampara la importación o exportación de mercancías en México**. Es la declaración formal que hace el importador (o exportador) ante las autoridades aduaneras sobre la mercancía que está moviendo, el valor que declara, el régimen bajo el que la introduce, y los impuestos que se pagan o que quedan en suspenso.

El pedimento lo elabora y firma el **Agente Aduanal**, quien es el único autorizado por el SAT para despachar mercancías ante la aduana. Sin agente aduanal, no puedes tramitar un pedimento. Los agentes aduanales operan con una **patente** otorgada por el SAT y son responsables solidarios de la correcta declaración de la mercancía.

La base legal del pedimento se encuentra en la **Ley Aduanera** y sus reglamentos, así como en las **Reglas Generales de Comercio Exterior (RGCE)** emitidas anualmente por el SAT.

---

## 2. El número de pedimento y cómo interpretarlo

Cada pedimento tiene un número único con el siguiente formato:

```
AA  BBB  CCCC  DDDDDDD
```

Donde:
- **AA**: últimos dos dígitos del año de operación (ej. 24 para 2024)
- **BBB**: clave de la aduana por donde entró/salió la mercancía (ej. 240 para Nuevo Laredo, 480 para Manzanillo, 640 para el Aeropuerto Internacional de la Ciudad de México)
- **CCCC**: número de patente del agente aduanal (4 dígitos)
- **DDDDDDD**: número secuencial del pedimento (7 dígitos)

Ejemplo: `24-240-1234-0005678`

Este número es el identificador único del pedimento y se utiliza en cualquier consulta ante el SAT, la ANAM (Agencia Nacional de Aduanas de México) o en disputas legales.

---

## 3. Secciones principales de un pedimento

Un pedimento está estructurado en varias secciones. Aunque el formato puede variar ligeramente según el sistema del agente aduanal, las secciones esenciales son:

### 3.1 Encabezado del pedimento

Es la parte superior del documento. Contiene:

- **Tipo de operación**: clave que indica si es importación, exportación, etc. (ver sección 4)
- **Clave de pedimento**: subclasifica el tipo de operación (ej. A1 para importación/exportación definitiva)
- **RFC del importador/exportador**: tu RFC como empresa.
- **Fecha de pago**: fecha en que se pagaron los impuestos y derechos.
- **Aduana**: nombre y clave de la aduana donde se procesó.
- **Patente**: número de patente del agente aduanal.
- **Candado fiscal**: número de candado o sello de seguridad puesto al contenedor.
- **Número de guía o BL**: para carga marítima, el Bill of Lading (BL); para aérea, el AWB (Air Waybill); para terrestre, la carta porte.
- **País de origen y procedencia**: distinción importante, pues el origen determina el arancel aplicable (especialmente en tratados como el T-MEC).
- **Transportista y número de contenedor**: datos del vehículo o contenedor que trae la mercancía.

### 3.2 Datos del importador/exportador

- Nombre o razón social
- RFC y domicilio fiscal
- Número de registro en el padrón de importadores (obligatorio para importar)

### 3.3 Partidas

Es el corazón del pedimento. Cada línea de mercancía diferente constituye una partida. Cada partida contiene:

- **Número de secuencia**: número de partida (001, 002, 003...).
- **Fracción arancelaria**: código de 8 dígitos de la Tarifa IGIE. (Ver sección 5)
- **Descripción de la mercancía**: descripción en español de los bienes.
- **Cantidad y unidad de medida**: cantidad física declarada y la unidad del catálogo (kg, piezas, litros, etc.).
- **Valor en aduana**: valor declarado en dólares (USD), que es la base para calcular los impuestos.
- **Valor en moneda nacional**: equivalente en pesos según el tipo de cambio del DOF del día de pago.
- **Impuestos de la partida**: desglose de IGI, IVA, DTA, y otras contribuciones por partida.
- **País de origen**: clave del país donde se fabricó la mercancía.
- **Número de serie o marca**: para algunos bienes (electrónica, vehículos) es obligatorio declararlo.

### 3.4 Liquidación (caja de impuestos)

Es la sección donde se suman todos los impuestos a pagar por el pedimento completo:

- **IGI** (Impuesto General de Importación): el arancel
- **IVA**: Impuesto al Valor Agregado (generalmente 16%)
- **DTA** (Derecho de Trámite Aduanero)
- **PRE** (Prevalidación Electrónica de Datos): cuota por la validación del pedimento
- **Cuotas compensatorias**: si aplican (aranceles adicionales contra dumping)
- **IEPS**: Impuesto Especial sobre Producción y Servicios (para bebidas alcohólicas, tabacos, combustibles)

El pago de estos impuestos se realiza en un banco autorizado o mediante transferencia al SAT, generalmente el mismo día que se presenta el pedimento ante la aduana.

### 3.5 Observaciones y anexos

Notas especiales del agente aduanal, identificadores de permisos previos (si la mercancía requiere permiso de otra secretaría como SEMARNAT, COFEPRIS o SEDENA), y datos de cuarentena para productos agropecuarios.

---

## 4. Tipos de pedimento más comunes

La clave de pedimento define el régimen aduanero bajo el que entra o sale la mercancía:

| Clave | Tipo de operación | Descripción |
|---|---|---|
| A1 | Importación definitiva | Mercancía que entra a México para quedarse y se despacha para consumo interno |
| A1 | Exportación definitiva | Mercancía que sale de México de forma permanente |
| IT | Importación temporal | Mercancía que entra temporalmente (para maquila, reparación, exposición) sin pagar IGI |
| ET | Exportación temporal | Mercancía que sale temporalmente y regresará |
| V5 | Importación virtual | Transferencia entre empresas IMMEX sin movimiento físico en aduana |
| RT | Retorno de temporal | Regreso al extranjero de mercancía que entró con pedimento temporal |

Para la mayoría de las PYMEs importadoras, el pedimento más común es el **A1 de importación definitiva**: traes mercancía del extranjero, pagas impuestos, y la mercancía queda en México de forma permanente.

---

## 5. La fracción arancelaria: el código que lo rige todo

La **fracción arancelaria** es un código de 8 dígitos que clasifica cada tipo de mercancía según el **Sistema Armonizado de Designación y Codificación de Mercancías** (SA), un sistema internacional administrado por la Organización Mundial de Aduanas (OMA) y adoptado por México en la Tarifa IGIE.

La estructura de la fracción arancelaria es:

```
CC.DD.EE.FF
│  │  │  └─ Subpartida nacional (últimos 2 dígitos, específicos de México)
│  │  └──── Subpartida del SA (dígitos 5-6)
│  └─────── Partida (dígitos 3-4)
└────────── Capítulo (dígitos 1-2)
```

**Ejemplo**: `85.17.12.01`
- Capítulo 85: Máquinas, aparatos y material eléctrico
- Partida 8517: Teléfonos, incluidos los teléfonos móviles (celulares)
- Subpartida 8517.12: Teléfonos para redes celulares u otras redes inalámbricas
- Fracción nacional 8517.12.01: Teléfonos inteligentes (smartphones)

La fracción arancelaria determina:
1. La **tasa del IGI** (arancel) a pagar: puede ser 0%, 5%, 10%, 15%, 20% o incluso más.
2. Si la mercancía requiere **permisos previos** de otras secretarías.
3. Si aplican **cuotas compensatorias** (antidumping).
4. Las **restricciones y regulaciones no arancelarias** (NOM, cuarentenas, etc.).

Clasificar incorrectamente una mercancía puede significar pagar más impuestos de los debidos o —más grave— pagar menos y luego ser auditado y multado.

---

## 6. Los impuestos del comercio exterior

### 6.1 IGI (Impuesto General de Importación) — El arancel

Es el impuesto principal de la importación. Su tasa está establecida en la Tarifa IGIE para cada fracción arancelaria. Gracias a tratados de libre comercio como el **T-MEC** (con EUA y Canadá), el **TLCUEM** (con la Unión Europea) y otros 12 tratados que México tiene vigentes, muchas fracciones tienen tasa del **0%** cuando la mercancía es originaria del país con el que existe el tratado.

Para aplicar tasa preferencial del T-MEC, la mercancía debe cumplir con las **reglas de origen** del tratado y el importador debe tener la **Certificación de Origen** correspondiente.

**Base del IGI**: Valor en Aduana × Tipo de Cambio × Tasa IGI

### 6.2 IVA de Importación

El 16% de IVA se paga sobre la base de: Valor en Aduana + IGI + DTA + otras contribuciones. Este IVA es **acreditable** en la declaración mensual del IVA, siempre que la importación sea para actividades gravadas. Es decir, no es un costo; es un crédito fiscal que recuperas.

### 6.3 DTA (Derecho de Trámite Aduanero)

Es una cuota que se paga por el trámite de la importación ante la aduana. Para importaciones por aduana marítima o terrestre, la tasa es del **0.8%** sobre el valor en aduana, con un mínimo y un máximo establecidos en la Ley Federal de Derechos. Para importaciones aéreas, es del **0.4%**.

### 6.4 Cuotas Compensatorias

Se aplican a mercancías que el gobierno mexicano ha determinado que se importan a precios de dumping (precios artificialmente bajos que dañan a la industria nacional). Son determinadas por la Secretaría de Economía mediante resoluciones publicadas en el DOF. Pueden ser porcentajes muy elevados (50%, 100% o más) sobre el valor de la mercancía.

---

## 7. El valor en aduana: no siempre es el precio que pagaste

Este es uno de los puntos más importantes y menos entendidos. El **valor en aduana** es la base sobre la que se calculan los impuestos. En México, el método principal es el **Valor de Transacción** (artículo 64 de la Ley Aduanera): el precio que efectivamente se pagó o se pagará por la mercancía.

Sin embargo, a este precio se pueden sumar o ajustar:
- Fletes y seguros hasta el punto de entrada a México
- Comisiones
- Regalías relacionadas con la mercancía

Y se pueden excluir:
- El costo del flete dentro de México (después del punto de entrada)
- Los derechos e impuestos pagados en México

Si el agente aduanal detecta que el valor declarado es anormalmente bajo respecto al precio de mercado, la aduana puede rechazarlo y usar métodos alternativos de valoración, lo que generalmente resulta en más impuestos.

---

## 8. El padrón de importadores: requisito previo

Para poder importar en México, tu empresa debe estar inscrita en el **Padrón de Importadores** del SAT. El trámite se realiza en el portal del SAT y requiere que la empresa esté al corriente de sus obligaciones fiscales y que su RFC esté activo.

Para algunos sectores (acero, textil, electrónica, bebidas alcohólicas, etc.) existe el **Padrón de Importadores de Sectores Específicos (PISE)**, que requiere requisitos adicionales.

Sin estar en el padrón, el agente aduanal no puede tramitar el pedimento a tu nombre.

---

## Resumen del capítulo

- El pedimento es el documento legal que ampara toda importación o exportación en México, elaborado y firmado por un agente aduanal con patente del SAT.
- El número de pedimento tiene formato: año-aduana-patente-secuencial.
- Las secciones principales son: encabezado, datos del importador, partidas, liquidación y observaciones.
- El tipo de pedimento más común para PYMEs es el A1 de importación definitiva.
- La fracción arancelaria (8 dígitos de la Tarifa IGIE) determina el arancel, los permisos requeridos y las regulaciones aplicables.
- Los impuestos principales son: IGI (arancel), IVA (acreditable), DTA y cuotas compensatorias.
- El IVA de importación se paga pero es acreditable; el IGI y el DTA son costos definitivos.
- Para importar, la empresa debe estar inscrita en el Padrón de Importadores del SAT.

---

*MYSTIC Academy — Importaciones y Comercio Exterior — Capítulo 1*
*Contenido elaborado con base en la Ley Aduanera, la Tarifa IGIE, el Código Fiscal de la Federación y las Reglas Generales de Comercio Exterior vigentes.*
