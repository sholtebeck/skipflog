import PickList from './PickList';
//import Table from 'react-bootstrap/Table';

const PicksTable = ({ pickers }) => (
<table className="pick-table">
<thead>
    <tr className="heading">
    {pickers.map(picker => (
        <th key={picker.name} className="table-header">{picker.name}</th>
    ))}        
    </tr>
</thead>
<tbody>
    <tr className="table-row" key="picks">
    {pickers.map(picker => (
        <td className="table-data"><PickList picker={picker} />
		</td>
    ))}
    </tr>
</tbody>
</table>
);

export default PicksTable;