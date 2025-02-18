import * as _ from 'lodash';

export const _cloneDeep = (value) => {
    return _.cloneDeep(value)
}

export const _assign = (object, ...sources) => {
    return _.assign({}, object, ...sources)
}

export const _isEqual = (value, other) => {
    return _.isEqual(value, other);
}

export const _pick = (object, paths) => {
    return _.pick(object, paths)
}

export const _omit = (object, paths) => {
    return _.omit(object, paths)
}

export const _lte = (value, other) => {
    return _.lte(value, other)
}
export const _gte = (value, other) => {
    return _.gte(value, other)
}

export const _call = (method, ...args) => {
    if(!method || !(`${method}` in _)) {
        console.error(`lodash does not have this method: ${method}`)
        return
    }
    return _[method](...args)
}

export const setValueByPath = (object, path, value) => {
    _.set(object, path, value)
}
export const getValueByPath = (object, path, defaultValue?) => {
    _.get(object, path, defaultValue)
}
export const findBy = (collection, condition, fromIndex=0) => {
    return _.find(collection, condition, fromIndex)
}
export const findIndex = (array, condition, fromIndex=0) => {
    return _.findIndex(array, condition, fromIndex)
}

export const objectHasKey = (object, path) => {
    return _.has(object, path)
}

export const objectMerge = (source, ...targets) => {
    return _.assign(source, ...targets)
}
export const objectIs= (value, other) => {
    return _.eq(value, other)
}
export const isObjectEmpty = (o) => _.isEmpty(o)