import React from "react"
import { v4 } from "uuid"

const Button = ({history, children}) =>
    <button className="btn btn-default btn-block"
            onClick={() => history.push('/customers')}>
        {children}
    </button>


const CustomerButton = ({customers, history, intl}) =>
    <div>
        {
            <Button history={history}>
                <i className="fa fa-user x2"></i> {' '}
                {
                    (customers.selectedID) ? 
                    customers.data[customers.selectedID].display_name : 'Customer'
                }
            </Button>
        }
    </div>


export default CustomerButton