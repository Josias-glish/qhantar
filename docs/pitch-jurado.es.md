# Pitch para el jurado (3 min 40 s)

**Ámbito:** exposición ante un jurado (NASA Space Apps 2026), voz propia, trato de usted.
Todas las cifras salen de `results/*/results.json`. Unas 475 palabras, a 130 palabras por minuto: 3 min 40 s.

---

Imagine un radar de velocidad al borde de la carretera. Un auto viene de frente y el radar marca su velocidad exacta. [pausa]
Otro auto cruza de lado, igual de rápido. Y el radar marca casi **cero**.

¿Ese auto estaba quieto? No. El radar **no podía verlo**.

Con los satélites radar pasa lo mismo. Y en La Paz, donde las laderas se mueven, eso importa.

NISAR, la nueva misión de NASA e ISRO, mide el movimiento del terreno. Pero solo mide la parte que va hacia el satélite o se aleja de él. Si una ladera se desliza de lado respecto a esa línea de visión, el interferograma puede verse tranquilo, aunque la ladera se esté moviendo.

Entonces aparecen dos errores. El primero: ver colores en la imagen y creer que hay movimiento sin revisar la calidad. El segundo: no ver nada y concluir que la ladera está quieta. [pausa] El segundo es el peligroso.

Por eso construimos **QHANTAR**.

QHANTAR toma un producto NISAR real, con los vectores de línea de visión que trae el propio archivo, y los cruza con la forma de cada ladera. Después revisa la calidad medida en esa pareja de imágenes. Y a cada píxel le asigna uno de cuatro estados: interpretable; visible pero sin calidad; con calidad pero casi ciego al movimiento; o no observable.

No detecta deslizamientos. No predice desastres. Responde una sola pregunta: **¿esta observación podía ver ese movimiento, sí o no, y por qué?**

Lo probamos con una escena real sobre La Paz, de octubre de 2026. El 35,5 % del recorte es interpretable. Pero fíjese en esto: el **23,6 %** tiene buena calidad y aun así casi no vería un movimiento ladera abajo. Ahí, un interferograma tranquilo **no prueba nada**.

Y como una sola órbita mira desde un solo lado, procesamos también la pasada descendente. Sola, deja interpretable el 39,1 %. Juntas, las dos órbitas llegan al **54,5 %**. [pausa] Mirar desde los dos lados cambia la respuesta.

Y queremos que sepa algo. [pausa] Publicamos también lo que no salió.

Teníamos una hipótesis: que las zonas con distorsión geométrica tienen peor calidad. La prueba que fijamos antes de mirar los datos dijo que sí. Pero al comparar con laderas igual de empinadas, la diferencia desaparece. Era la pendiente, no la distorsión. Un resultado negativo también es evidencia.

Y un índice independiente de la literatura coincide con nuestro modelo: un kappa de 0,88.

La idea de cruzar pendiente y radar no es nuestra. Ya existe en los trabajos de Notti y de van Natijne. Lo que hacemos es aplicarla después de la observación, sobre una pareja NISAR concreta, con su geometría nativa y su calidad medida.

El código, las pruebas y cada cifra están abiertos.

Porque en la montaña, no ver una señal no siempre significa que no haya movimiento. [pausa]
A veces significa que el radar **no podía verlo**. QHANTAR le dice cuándo.

---

## Opciones de apertura

1. **El radar de la policía** (la del guion). Funciona porque todo el mundo ha visto uno: el jurado entiende la línea de visión en diez segundos, sin una sola fórmula.
2. **Pregunta directa:** «Si un satélite mira una ladera y no ve movimiento, ¿usted diría que la ladera está quieta?» [pausa] «Nosotros tampoco, y le vamos a mostrar por qué.» Funciona porque pone al jurado a pensar el error antes de que usted lo explique.

## Opciones de cierre

1. **«A veces significa que el radar no podía verlo. QHANTAR le dice cuándo.»** (la del guion). Funciona porque vuelve a la imagen del inicio y cierra el círculo.
2. **«Antes de confiar en lo que el radar muestra, hay que saber lo que el radar podía ver. Eso es QHANTAR.»** Funciona porque deja una frase corta que el jurado puede repetir al deliberar.
