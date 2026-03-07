import relativeTime from 'dayjs/plugin/relativeTime';
import dayjs from 'dayjs';

dayjs.extend(relativeTime);

type LateStatus = {
    status: "late" | "onTime";
    from: string;
};

export function checkLateStatus(time: string, currentLocale: string, comparing?: string, removeSuffex: boolean = false): LateStatus {
    let comparable: dayjs.Dayjs;
    if (comparing) {
        comparable = dayjs(comparing);
    } else {
        comparable = dayjs();
    }

    const deadLine = dayjs(time).locale(currentLocale);

    if (comparable.isAfter(deadLine)) {
        return {
            status: "late",
            from: deadLine.from(comparable, removeSuffex)
        };
    }
    return {
        status: "onTime",
        from: deadLine.from(comparable, removeSuffex)
    };
}

export default dayjs;
