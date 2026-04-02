# Capítulo 1: Anatomía de una factura electrónica
### Curso: Facturación CFDI 4.0 sin errores — MYSTIC Academy

---

## Introducción

En México, cada vez que vendes un producto o prestas un servicio, tienes la obligación de emitir un Comprobante Fiscal Digital por Internet, mejor conocido como **CFDI**. Desde enero de 2022, la versión vigente es el **CFDI 4.0**, que trajo cambios significativos respecto a la versión 3.3 que la mayoría de los negocios usaban desde 2017.

Una factura electrónica incorrecta puede significar que tu cliente no pueda deducirla. Una cancelación mal hecha puede generarte una multa. Un complemento omitido puede desencadenar un requerimiento del SAT. El CFDI no es un simple "recibo": es un documento legal con validez probatoria y fiscal.

En este capítulo diseccionamos una factura electrónica campo por campo para que nunca más emitas un CFDI a ciegas.

---

## 1. ¿Qué es un CFDI?

El CFDI (Comprobante Fiscal Digital por Internet) es el documento que acredita una transacción comercial ante el SAT. Su base técnica es un archivo **XML** firmado digitalmente, que contiene información estructurada de la operación y que es certificado por un **Proveedor Autorizado de Certificación (PAC)**.

El proceso es el siguiente:
1. Tú o tu sistema generan el XML con los datos de la operación.
2. El XML se envía al PAC de tu elección.
3. El PAC valida que el XML cumpla con la estructura del Anexo 20 del SAT.
4. El PAC le agrega el **Timbre Fiscal Digital (TFD)**, que contiene el sello del SAT y el UUID.
5. El XML timbrado regresa a tu sistema y se puede representar en PDF para entregar al cliente.

El archivo que tiene valor legal es el **XML**, no el PDF. El PDF es solo una representación visual para facilitar la lectura humana.

---

## 2. Tipos de CFDI que existen

El Anexo 20 define 5 tipos de CFDI según el tipo de operación:

| Tipo | Clave | Para qué sirve |
|---|---|---|
| Ingreso | I | Ventas de bienes o servicios |
| Egreso | E | Descuentos, devoluciones, bonificaciones |
| Traslado | T | Amparar la transportación de mercancías |
| Nómina | N | Pago de sueldos y salarios a empleados |
| Pago | P | Recibir el pago de facturas emitidas a crédito |

El CFDI de tipo **Ingreso** es el más común —la factura de venta ordinaria—. El CFDI de tipo **Pago** (con su complemento de Recepción de Pagos) se emite cuando cobras una factura que originalmente se emitió con método de pago "PPD" (Pago en Parcialidades o Diferido).

---

## 3. La estructura del CFDI 4.0: campo por campo

El CFDI 4.0 está definido en el **Anexo 20** de la Resolución Miscelánea Fiscal. Su estructura XML tiene nodos principales que contienen distintos tipos de datos.

### 3.1 Nodo Comprobante (el encabezado)

Es el nodo raíz del XML. Sus atributos más importantes son:

- **Version**: siempre "4.0" en la versión actual.
- **Fecha**: fecha y hora de emisión del CFDI en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS). No puede ser mayor a 72 horas antes del timbrado.
- **Serie y Folio**: identificadores propios del emisor para controlar sus folios internos. No son obligatorios, pero es buena práctica usarlos.
- **FormaPago**: catálogo del SAT con la forma en que se liquidó la operación. Ejemplos: 01 = Efectivo, 03 = Transferencia electrónica, 04 = Tarjeta de crédito, 28 = Tarjeta de débito.
- **MetodoPago**: PUE (Pago en Una Sola Exhibición) o PPD (Pago en Parcialidades o Diferido). Si pones PPD, deberás emitir un CFDI de Pago cuando cobres.
- **LugarExpedicion**: código postal del lugar donde se expide el CFDI (no necesariamente donde está el negocio; puede ser el del domicilio fiscal).
- **TipoDeComprobante**: I, E, T, N o P.
- **Moneda**: clave del catálogo SAT. MXN para pesos mexicanos, USD para dólares, EUR para euros.
- **TipoCambio**: requerido cuando la moneda no es MXN. Debe corresponder al tipo de cambio del Diario Oficial de la Federación (DOF) del día de la operación.
- **SubTotal**: suma de los importes de todas las partidas antes de descuentos e impuestos.
- **Total**: monto total del comprobante incluyendo impuestos y descuentos.

### 3.2 Nodo Emisor

Contiene los datos del que emite la factura:

- **Rfc**: RFC del emisor con homoclave. Para personas morales, 12 caracteres. Para personas físicas, 13 caracteres. Debe coincidir exactamente con el RFC registrado ante el SAT.
- **Nombre**: nombre o razón social tal como aparece en el RFC. En CFDI 4.0 este campo es obligatorio y la validación es más estricta que en la versión 3.3.
- **RegimenFiscal**: clave del catálogo del SAT que indica el régimen bajo el cual tributa el emisor. Ejemplos: 601 = General de Ley Personas Morales, 612 = Personas Físicas con Actividades Empresariales y Profesionales, 626 = Régimen Simplificado de Confianza.

### 3.3 Nodo Receptor

Datos de quien recibe la factura. En CFDI 4.0 este nodo se volvió mucho más estricto:

- **Rfc**: RFC del receptor. En operaciones con el público en general se usa el RFC genérico XAXX010101000. Para extranjeros, XEXX010101000.
- **Nombre**: nombre o razón social del receptor. **Novedad del CFDI 4.0**: el SAT valida que el nombre coincida con el RFC en su padrón. Si hay discrepancia, el PAC rechaza el timbrado.
- **DomicilioFiscalReceptor**: código postal del domicilio fiscal del receptor. **Novedad del CFDI 4.0**: es obligatorio y debe coincidir con el registrado ante el SAT.
- **RegimenFiscalReceptor**: régimen fiscal del receptor. **Novedad del CFDI 4.0**: también obligatorio, y debe ser congruente con el RFC del receptor.
- **UsoCFDI**: clave del catálogo del SAT que indica para qué usará el receptor la factura (qué va a deducir o acreditar). Algunos usos comunes: G01 = Adquisición de mercancias, G03 = Gastos en general, P01 = Por definir. En CFDI 4.0 el uso debe ser congruente con el régimen fiscal del receptor.

### 3.4 Nodo Conceptos

Lista de los productos o servicios facturados. Cada concepto tiene:

- **ClaveProdServ**: clave del catálogo del SAT (Catálogo de Productos y Servicios del CFDI) que describe la naturaleza del bien o servicio. Hay miles de claves; elegir la incorrecta puede causar problemas de deducción.
- **ClaveUnidad**: unidad de medida según el catálogo del SAT. Ejemplos: H87 = Pieza, KGM = Kilogramo, MTR = Metro, E48 = Servicio.
- **Cantidad**: número de unidades.
- **Descripcion**: descripción del bien o servicio. Debe ser suficientemente específica; evita descripciones genéricas como "servicios varios".
- **ValorUnitario**: precio unitario antes de impuestos.
- **Importe**: Cantidad × ValorUnitario.
- **Descuento**: monto del descuento aplicado al concepto (si aplica).
- **Impuestos del concepto**: cada concepto puede tener sus propios traslados y retenciones de impuestos.

### 3.5 Nodo Impuestos

Resumen de los impuestos del comprobante:

- **TotalImpuestosTraladados**: suma de todos los impuestos que el emisor traslada al receptor (normalmente IVA).
- **TotalImpuestosRetenidos**: suma de impuestos que el emisor retiene al receptor (ISR retenido, IVA retenido en servicios profesionales o arrendamiento).

Los impuestos en el CFDI 4.0 se declaran a nivel de concepto y se consolidan en este nodo.

### 3.6 Nodo TimbreFiscalDigital (TFD)

Es el complemento que agrega el PAC durante el timbrado. Contiene:

- **UUID**: identificador único universal del comprobante. Es una cadena de 36 caracteres en formato hexadecimal separada por guiones. **Este es el folio fiscal**; no el folio interno del emisor.
- **FechaTimbrado**: fecha y hora exacta en que el PAC certificó el CFDI.
- **RfcProvCertif**: RFC del PAC que realizó el timbrado.
- **SelloCFD**: sello digital del emisor (generado con su certificado de sello digital).
- **SelloSAT**: sello del SAT que autentica el timbrado.
- **NoCertificadoSAT**: número de certificado del SAT usado para generar el sello del SAT.

---

## 4. El UUID: el folio fiscal que importa

El UUID (Universally Unique Identifier) es el número que identifica de manera única cada CFDI en el universo fiscal mexicano. Cuando el SAT habla de "folio fiscal", se refiere al UUID.

Ejemplo de UUID: `6B02A2F5-3D21-4B8C-A912-00E1A3D47892`

Para verificar si un CFDI es auténtico, el SAT ofrece el **Verificador de CFDI** en:
`https://verificacfdi.facturaelectronica.sat.gob.mx/`

Solo necesitas el UUID, el RFC del emisor, el RFC del receptor y el monto total para verificar cualquier factura.

---

## 5. Complementos del CFDI

Los complementos son nodos XML adicionales que se agregan al CFDI para reportar información específica de ciertos sectores o tipos de operación. Los más comunes son:

- **Complemento de Pago (REP)**: para facturas cobradas con PPD.
- **Complemento de Nómina (versión 1.2)**: para CFDI de tipo Nómina.
- **Complemento de Carta Porte**: obligatorio para el transporte de mercancías por carretera desde junio de 2022.
- **Complemento de Comercio Exterior**: para operaciones de exportación.
- **Complemento de Instituciones Educativas**: para escuelas.
- **Complemento de Hidrocarburos**: para gasolineras.

Omitir un complemento obligatorio puede invalidar el CFDI o generar sanciones.

---

## 6. Errores más comunes al emitir CFDI 4.0

Desde que entró en vigor el CFDI 4.0 en enero de 2022, los siguientes errores son los más frecuentes:

1. **Nombre del receptor no coincide con el SAT**: el receptor debe proporcionar su nombre exactamente como aparece en su Constancia de Situación Fiscal. Un acento diferente puede causar el rechazo.

2. **Código postal del receptor incorrecto**: muchos clientes no conocen su domicilio fiscal actualizado ante el SAT.

3. **Uso del CFDI incongruente con el régimen**: por ejemplo, poner uso G01 (Adquisición de mercancias) a un receptor en RESICO que no puede deducir compras de mercancía.

4. **Método de pago incorrecto**: poner PUE cuando la factura se pagará a crédito, o viceversa. Si pones PUE, el SAT asume que ya cobré; si en realidad cobro después, no puedo emitir el complemento de pago.

5. **ClaveProdServ demasiado genérica**: usar claves como "84111506 - Servicios de contabilidad" cuando en realidad se vende maquinaria genera inconsistencias.

6. **No cancelar correctamente**: en CFDI 4.0, para cancelar una factura que ya fue aceptada por el receptor, generalmente se necesita su autorización. El proceso de cancelación también tiene plazos.

---

## 7. Certificados de Sello Digital (CSD)

Para emitir CFDI necesitas un **Certificado de Sello Digital (CSD)**, diferente a la e.firma (FIEL). El CSD se genera en el portal del SAT (CertiSAT Web) y tiene vigencia de 4 años. Cuando vence, no puedes timbrar.

El CSD consta de:
- Un archivo `.cer` (certificado público)
- Un archivo `.key` (llave privada, protegida con contraseña)

Estos archivos se cargan en tu sistema de facturación o se entregan al PAC para que selle los CFDI en tu nombre.

---

## Resumen del capítulo

- El CFDI es el documento fiscal legal en México; el XML es el original y el PDF solo es representación visual.
- Existen 5 tipos de CFDI: Ingreso, Egreso, Traslado, Nómina y Pago.
- El CFDI 4.0 obligó a validar el nombre, código postal y régimen fiscal del receptor con el padrón del SAT.
- El UUID es el folio fiscal único que identifica cada comprobante en el sistema del SAT.
- Los complementos agregan información específica según el tipo de operación.
- Los errores más comunes se concentran en los datos del receptor y en el método de pago.
- Para emitir CFDI se necesita un Certificado de Sello Digital (CSD) vigente.

---

*MYSTIC Academy — Facturación CFDI 4.0 sin errores — Capítulo 1*
*Contenido elaborado con base en el Anexo 20 de la Resolución Miscelánea Fiscal y la Ley del CFF vigentes.*
