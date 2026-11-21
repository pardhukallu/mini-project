// Client-side email validation that mirrors the backend's EmailStr rules.
// Keeping both layers aligned avoids sending malformed addresses to the API.

const LOCAL_PART_RE =
  /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*$/;
const DOMAIN_LABEL_RE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/;
const TLD_RE = /^(?:[A-Za-z]{2,}|xn--[A-Za-z0-9-]{2,})$/;

/**
 * Returns a human-readable error message for an invalid address,
 * or null when the address is acceptable.
 */
export function validateEmail(raw: string): string | null {
  const value = raw.trim();

  if (!value) {
    return 'Please enter an email address.';
  }

  if (value.length > 254) {
    return 'Please enter a valid email address.';
  }

  const atIndex = value.lastIndexOf('@');
  if (atIndex <= 0 || atIndex !== value.indexOf('@') || atIndex === value.length - 1) {
    return 'Please enter a valid email address, for example name@example.com.';
  }

  const localPart = value.slice(0, atIndex);
  const domain = value.slice(atIndex + 1).toLowerCase();

  if (localPart.length > 64 || !LOCAL_PART_RE.test(localPart)) {
    return 'Please enter a valid email address, for example name@example.com.';
  }

  const labels = domain.split('.');
  if (labels.length < 2 || labels.some((label) => !DOMAIN_LABEL_RE.test(label))) {
    return 'Please enter a valid email address, for example name@example.com.';
  }

  const tld = labels[labels.length - 1];
  if (!TLD_RE.test(tld)) {
    return 'Please enter a valid email address with a real domain extension, for example name@example.com.';
  }

  return null;
}
