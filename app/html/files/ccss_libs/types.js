class ArrayOfNumbers extends Array {
    constructor() {
        super();
    }

    pushNumber(item) {
        item *= 1;
        if (isFinite(item)) this.push(item);
    }

    sum() {
        return this.reduce((accumulator, currentValue) => accumulator + currentValue, 0)
    }

    sum(valueNumber) {
        this.forEach((value, index) => this[index] = value + valueNumber)
    }

    non_zeros() {
        return this.reduce(
            (accumulator, currentValue) => {
                if (currentValue > 0) {
                    return accumulator + 1;
                }
                return accumulator;
            }, 0
        )
    }

    log() {
        console.log(this);
    }
}

