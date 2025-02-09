export function cutStringByHtmlTag(inputString: string, htmlTagList: string[]): [string, string] {
    for (const tag of htmlTagList) {
        const result = inputString.split(tag)[1];
        if (result.length > 1) {
            const closedTag = insertSlashAtSecondPosition(tag);
            return [result.split(closedTag)[0], closedTag];
        }
    }
    return [inputString, '']
}

function insertSlashAtSecondPosition(input: string): string {
    return `${input.slice(0, 1)}/${input.slice(1)}`;
}
