const PickList = ({ picker,next }) => (
    <ol>
    {picker.picks.map(pick => (
        <li key={pick}>{pick}</li>
    ))}

    </ol>
);
export default PickList;