import en from "./locales/en.json";
import hi from "./locales/hi.json";
import bn from "./locales/bn.json";
import mr from "./locales/mr.json";

export const translations = {
  en,
  hi,
  bn,
  mr,
};

export function translate(language, key) {
  const locale = translations[language] ?? translations.en;

  const value = key
    .split(".")
    .reduce((current, part) => current?.[part], locale);

  if (value !== undefined) {
    return value;
  }

  const fallback = key
    .split(".")
    .reduce(
      (current, part) => current?.[part],
      translations.en
    );

  return fallback ?? key;
}