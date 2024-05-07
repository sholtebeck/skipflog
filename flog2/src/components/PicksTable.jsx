import PickList from './PickList';

const PicksTable = ({ pickers, next }) => (
<table className="pick-table">
<thead>
    <tr className="heading">
    {pickers.map(picker => (
        <th key={picker.name} className="table-header">{picker.name}</th>
    ))}        
    </tr>
</thead>
<tbody>
    <tr key="picks">
    {pickers.map(picker => (
        <td><PickList picker={picker} next={picker.name == next && picker.picks.length<10 } /> 
        {picker.altpick && <div>Alt: {picker.altpick}</div>}
        </td>
    ))}

    </tr>
</tbody>
</table>
);

export default PicksTable;