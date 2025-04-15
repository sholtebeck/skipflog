const PickList = ({ picker }) => (
    <>
    <ol class="list-group-numbered">
    {picker.picks.map(pick => (
        <li class="list-group-item left ml-1" key={pick}>{pick}</li>
    ))}
    </ol>
    </>
);
export default PickList;