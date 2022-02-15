/**
 * Very simple email validation
 * @param {String} text - email to be validated
 * @return boolean
 */
export function validateEmail(text) {
    return text?.indexOf("@") !== -1
}

/**
 * ensures password is at least certain length
 * 
 * @param {String} password - password to be validated
 * @param {Integer} length - length password must be long as
 * @return {Boolean}
 */
export function validatePassword(password, length = 7) {
    return password?.length >= length
}

export function validateUsername(username) {
    return /^[a-zA-Z0-9_-]+$/.test(username)
}

export default {
    email: validateEmail,
    password: validatePassword,
    username: validateUsername
}