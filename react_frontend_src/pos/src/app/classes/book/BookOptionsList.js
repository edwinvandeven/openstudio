import React from "react"
import { v4 } from "uuid"

import BookOptionsListItemClasscard from "./BookOptionsListItemClasscard"
import BookOptionsListItemDropin from "./BookOptionsListItemDropin"
import BookOptionsListItemSubscription from "./BookOptionsListItemSubscription"
import BookOptionsListItemTrial from "./BookOptionsListItemTrial"
import BookOptionsListItemComplementary from "./BookOptionsListItemComplementary"
import BookOptionsListItemReconcileLater from "./BookOptionsListItemReconcileLater"

const populateRowsSubscriptions = (subscriptions, customer_memberships, onClick=f=>f) => {
    let container = []
    let children = []
    subscriptions.map((subscription, i) => {
        children.push(<BookOptionsListItemSubscription key={"subscription_" + v4()}
                                                       data={subscription}
                                                       customer_memberships={customer_memberships}
                                                       onClick={() => onClick(subscription)} />)
        if (( (i+1) % 4 ) === 0 || i+1 == subscriptions.length)  {
            container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
            children = []
        }
    })
           
    return container
}

const populateRowsClasscards = (classcards, customer_memberships, onClick=f=>f) => {
    let container = []
    let children = []
    classcards.map((classcard, i) => {
        children.push(<BookOptionsListItemClasscard key={"classcard_" + v4()}
                                                       data={classcard}
                                                       customer_memberships={customer_memberships}
                                                       onClick={() => onClick(classcard)} />)
        if (( (i+1) % 4 ) === 0 || i+1 == classcards.length)  {
            container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
            children = []
        }
    })
           
    return container
}

const BookOptionsList = ({booking_options, customer_memberships, onClick=f=>f}) => 
    <div className="classes-booking-options">
        {console.log('booking options list props')}
        {console.log(booking_options)}
        {console.log(customer_memberships)}
        {(booking_options.subscriptions.length > 0) ?
            <div>
                <h4>Subscriptions</h4>
                <div>
                    { populateRowsSubscriptions(booking_options.subscriptions, customer_memberships, onClick) }
                </div>
            </div>
        : '' }
        {(booking_options.classcards.length > 0) ?
            <div>
                <h4>Class cards</h4>
                <div>
                    { populateRowsClasscards(booking_options.classcards, customer_memberships, onClick) }
                </div>
            </div>
        : '' }
        <h4>Drop-in & Trial</h4>
        <div className="row">
            {(booking_options.dropin_and_membership) ? 
                <BookOptionsListItemDropin data={booking_options.dropin_and_membership}
                                           customer_memberships={customer_memberships}
                                           onClick={onClick} /> : ""   
            } 
            <BookOptionsListItemDropin data={booking_options.dropin}
                                       customer_memberships={customer_memberships}
                                       onClick={onClick} />                          
            <BookOptionsListItemTrial data={booking_options.trial}
                                      onClick={onClick} />
        </div>
        <h4>Other</h4>
        <div className="row">
            {(booking_options.complementary) ?
                <BookOptionsListItemComplementary data={booking_options.complementary}
                                                  onClick={onClick} />
                : ""
            }
            {(booking_options.reconcile_later) ?
                <BookOptionsListItemReconcileLater data={booking_options.reconcile_later}
                                                   onClick={onClick} />
            : "" }
        </div>
    </div>


export default BookOptionsList