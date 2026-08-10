/** Project languages — mirror backend ``Language`` enum (REQ-132, REQ-139). */
export const LANGUAGES = ["hi", "mr", "ta"] as const;

export type LanguageCode = (typeof LANGUAGES)[number];

export function isLanguageCode(value: string): value is LanguageCode {
  return (LANGUAGES as readonly string[]).includes(value);
}
