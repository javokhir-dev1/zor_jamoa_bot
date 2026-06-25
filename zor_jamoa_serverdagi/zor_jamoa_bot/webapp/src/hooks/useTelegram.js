const tg = window.Telegram?.WebApp;

export function useTelegram() {
  const initData   = tg?.initData ?? "";
  const user       = tg?.initDataUnsafe?.user ?? null;
  const colorScheme = tg?.colorScheme ?? "light";

  function ready()  { tg?.ready(); }
  function expand() { tg?.expand(); }
  function close()  { tg?.close(); }

  function showAlert(msg, cb)   { tg?.showAlert(msg, cb); }
  function showConfirm(msg, cb) { tg?.showConfirm(msg, cb); }

  function haptic(type = "light") {
    tg?.HapticFeedback?.impactOccurred(type);
  }

  return { tg, initData, user, colorScheme, ready, expand, close, showAlert, showConfirm, haptic };
}
