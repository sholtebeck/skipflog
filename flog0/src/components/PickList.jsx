const PickList = ({ picker }) => (
    <>
    <ol>
    {picker.picks.map(pick => (
        <li className="left" key={pick}>{pick}</li>
    ))}
    </ol>
    </>
);
export default PickList;