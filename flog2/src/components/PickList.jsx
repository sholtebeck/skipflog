const PickList = ({ picker }) => (
    <ol>
    {picker.picks.map(pick => (
        <li key={pick}>{pick}</li>
    ))}
    </ol>
);
export default PickList;