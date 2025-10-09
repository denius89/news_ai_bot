export const initHoloMotion = (deviceOrientation?: { alpha: number; beta: number; gamma: number }) => {
  const layer = document.querySelector(".holo-surface");
  if (!layer) return;

  if (deviceOrientation) {
    // Используем данные из React state
    const { beta, gamma } = deviceOrientation;
    const x = gamma || 0;
    const y = beta || 0;
    const rotation = (x + y) / 4;
    layer.setAttribute(
      "style",
      `background: linear-gradient(${rotation + 180}deg, rgba(0,191,166,0.15), rgba(22,184,126,0.15), rgba(166,246,209,0.15));`
    );
  } else {
    // Fallback: слушаем события напрямую
    const handleOrientationChange = (event: DeviceOrientationEvent) => {
      const x = event.gamma || 0;
      const y = event.beta || 0;
      const rotation = (x + y) / 4;
      layer.setAttribute(
        "style",
        `background: linear-gradient(${rotation + 180}deg, rgba(0,191,166,0.15), rgba(22,184,126,0.15), rgba(166,246,209,0.15));`
      );
    };

    window.addEventListener("deviceorientation", handleOrientationChange);
    
    // Возвращаем функцию очистки
    return () => {
      window.removeEventListener("deviceorientation", handleOrientationChange);
    };
  }
};
