# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.user.id == 1)
def test_extend_validity():
    """
    Function to expose class & method used by scheduler task
    to create monthly invoices
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()

    valid_on = request.vars['valid_on']
    days_to_add = request.vars['days_to_add']

    ost.customers_classcards_extend_validity(valid_on, days_to_add)