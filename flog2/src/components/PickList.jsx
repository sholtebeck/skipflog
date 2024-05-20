const PickList = ({ picker,next }) => (
    <ol className="table-top">
    {picker.picks.map(pick => (
        <li key={pick}>{pick}</li>
    ))}
    {next && <li/>}
    </ol>
);
export default PickList;