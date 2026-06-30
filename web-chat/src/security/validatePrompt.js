/**
 * Validation des entrees utilisateur — aligne sur scripts/data_validator.py (equipe DATA/CYBER).
 */

const FORBIDDEN = [
  'ignore previous',
  'oublie',
  'bypass',
  'system prompt',
  'j3 su1s un3 p0up33 d3 c1r3',
  'poupée de cire',
  'poupee de cire',
  'x-compliance-token',
  'enhanced_mode',
  'enhanced mode',
];

const MAX_LENGTH = 1500;

export function validateUserPrompt(userInput) {
  if (typeof userInput !== 'string' || userInput.trim().length < 2) {
    return { isValid: false, error: 'Requete vide ou trop courte.' };
  }

  if (userInput.length > MAX_LENGTH) {
    return { isValid: false, error: 'Requete trop longue (max 1500 caracteres).' };
  }

  const lower = userInput.toLowerCase();
  if (FORBIDDEN.some((f) => lower.includes(f))) {
    return { isValid: false, error: 'Tentative de jailbreak ou contenu interdit detecte.' };
  }

  const cleanPrompt = userInput.replace(/<[^>]*>/g, '').trim();
  return { isValid: true, cleanPrompt };
}

export function checkResponseHeaders(headers) {
  const suspicious = [];
  headers.forEach((value, key) => {
    if (key.toLowerCase().startsWith('x-') && key.toLowerCase().includes('compliance')) {
      suspicious.push(key);
    }
  });
  return suspicious;
}
