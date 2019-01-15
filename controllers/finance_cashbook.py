# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def index():
    """

    :return:
    """
    response.title = T('Cash book')

    if session.finance_cashbook_date:
        date = session.finance_cashbook_date
    else:
        date = TODAY_LOCAL
        session.finance_cashbook_date = date

    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT)
    )
    response.view = 'general/only_content_no_box.html'

    debit = get_debit(date)
    debit_total = debit['total']

    credit = get_credit(date)
    credit_total = credit['total']

    balance = index_get_balance(debit_total, credit_total)

    content = DIV(
        balance,
        debit['column_content'],
        credit['column_content'],
        _class='row'
    )

    header_tools = DIV(
        get_day_chooser(date)
    )

    return dict(
        content=content,
        header_tools=header_tools
    )


def get_debit(date):
    """
    Populate the credit column
    :param date: datetime.date
    :return: dict['total'] & dict['column_content']
    """
    total = 0

    # Cash count opening balance
    count_opening = cash_count_get(date, 'opening')
    total += count_opening['total']

    # Additional items
    additional_items = additional_items_get(date, 'debit')
    total += additional_items['total']

    # Class balance (total revenue - teacher payments)
    classes_balance = get_debit_classes(date, 'balance')
    total += classes_balance['total']

    # Sold memberships
    sold_memberships = get_debit_memberships(date)
    total += sold_memberships['total']

    # Sold cards
    sold_cards = get_debit_classcards(date)
    total += sold_cards['total']

    # Sold products
    sold_products = get_debit_sales_summary(date)
    total += sold_products['total']

    # Class teacher payments
    teacher_payments = get_debit_classes(date, 'teacher_payments')
    total += teacher_payments['total']


    column = DIV(
        H4(T("Income")),
        count_opening['box'],
        additional_items['box'],
        classes_balance['box'],
        sold_memberships['box'],
        sold_cards['box'],
        sold_products['box'],
        teacher_payments['box'],
        _class=' col-md-6'

    )

    return dict(
        total = total,
        column_content = column
    )


def get_credit(date):
    """
    Populate the credit column
    :param date: datetime.date
    :return: dict['total'] & dict['column_content']
    """
    total = 0

    # Cash count closing balance
    count_closing = cash_count_get(date, 'closing')
    total += count_closing['total']

    # Additional items
    additional_items = additional_items_get(date, 'credit')
    total += additional_items['total']

    # Classes used on cards
    cards_used_classes = get_credit_classcards_used_classes_summary(date)
    total += cards_used_classes['total']

    column = DIV(
        H4(T("Expenses")),
        count_closing['box'],
        additional_items['box'],
        cards_used_classes['box'],
        _class=' col-md-6'
    )

    return dict(
        total = total,
        column_content = column
    )


def additional_items_get(date, booking_type):
    """

    :param date:
    :return: dict
    """
    from openstudio.os_accounting_cashbooks_additional_items import AccountingCashbooksAdditionalItems

    acai = AccountingCashbooksAdditionalItems()
    result = acai.list_formatted(date, date, booking_type)
    acai_debit_list = result['table']
    acai_debit_total = result['total']

    if booking_type == 'debit':
        box_class = 'box-success'
    elif booking_type == 'credit':
        box_class = 'box-danger'

    link_add = ''
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('create', 'accounting_cashbooks_additional_items'):
        link_add = SPAN(
            SPAN(XML(" &bull; "), _class='text-muted'),
            A(T("Add item"),
              _href=URL('additional_item_add', vars={'booking_type': booking_type}))
        )


    additional_items = DIV(
        DIV(H3("Additional items", _class='box-title'),
            link_add,
            DIV(
                A(I(_class='fa fa-minus'),
                  _href='#',
                  _class='btn btn-box-tool',
                  _title=T("Collapse"),
                  **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'
            ),
            _class='box-header'),
        DIV(acai_debit_list, _class='box-body no-padding'),
        _class='box ' + box_class
    )

    return dict(
        box = additional_items,
        total = acai_debit_total
    )


def index_get_balance(debit_total=0, credit_total=0):
    """

    :return:
    """
    balance = debit_total - credit_total
    balance_class = ''
    if balance < 0:
        balance_class = 'text-red bold'

    box = DIV(DIV(
        DIV(
            H3(T("Summary"), _class='box-title'),
            _class='box-header'
        ),
        DIV(DIV(DIV(DIV(H5(T("Income"), _class='description-header'),
                        SPAN(represent_float_as_amount(debit_total), _class='description-text'),
                        _class='description-block'),
                    _class='col-md-4 border-right'),
                DIV(DIV(H5(T("Expenses"), _class='description-header'),
                        SPAN(represent_float_as_amount(credit_total), _class='description-text'),
                        _class='description-block'),
                    _class='col-md-4 border-right'),
                DIV(DIV(H5(T("Balance"), _class='description-header'),
                        SPAN(represent_float_as_amount(balance), _class='description-text ' + balance_class),
                        _class='description-block'),
                    _class='col-md-4'),
                _class='row'),
            _class='box-footer'
        ),
        _class='box box-primary'
    ), _class='col-md-12')

    return box


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def set_date():
    """
    Set date for cashbook
    :return:
    """
    from general_helpers import datestr_to_python

    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, request.vars['date'])

    session.finance_cashbook_date = date

    redirect(URL('index'))


def get_day_chooser(date):
    """
    Set day for cashbook
    :param date: datetime.date
    :return: HTML prev/next buttons
    """
    yesterday = (date - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
    tomorrow = (date + datetime.timedelta(days=1)).strftime(DATE_FORMAT)

    link = 'set_date'
    url_prev = URL(link, vars={'date': yesterday})
    url_next = URL(link, vars={'date': tomorrow})
    url_today = URL(link, vars={'date': TODAY_LOCAL.strftime(DATE_FORMAT)})

    today = ''
    if date != TODAY_LOCAL:
        today = A(os_gui.get_fa_icon('fa fa-calendar-o'), ' ', T("Today"),
                 _href=url_today,
                 _class='btn btn-default')

    previous = A(I(_class='fa fa-angle-left'),
                 _href=url_prev,
                 _class='btn btn-default')
    nxt = A(I(_class='fa fa-angle-right'),
            _href=url_next,
            _class='btn btn-default')

    return DIV(previous, today, nxt, _class='btn-group pull-right')


def index_return_url(var=None):
    return URL('index')


@auth.requires_login()
def cash_count_add():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    count_type = request.vars['count_type']
    date = session.finance_cashbook_date

    if count_type == 'opening':
        count_type = T("opening")
    elif count_type == 'closing':
        count_type = T("closing")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Set %s count") % count_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    db.accounting_cashbooks_cash_count.CountDate.default = date
    db.accounting_cashbooks_cash_count.CountType.default = count_type

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_cashbooks_cash_count,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def cash_count_edit():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    ccID = request.vars['ccID']

    date = session.finance_cashbook_date
    cc = db.accounting_cashbooks_cash_count(ccID)
    if cc.CountType == 'opening':
        count_type = T("opening")
    elif cc.CountType == 'closing':
        count_type = T("closing")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Edit %s count") % count_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_cashbooks_cash_count,
        return_url,
        ccID,
        message_record_updated=T("Saved"),
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def additional_item_add():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    date = session.finance_cashbook_date
    db.accounting_cashbooks_additional_items.BookingDate.default = date

    booking_type = request.vars['booking_type']
    if booking_type == 'credit':
        db.accounting_cashbooks_additional_items.BookingType.default = 'credit'
        subtitle_type = T("Income")
    elif booking_type == 'debit':
        db.accounting_cashbooks_additional_items.BookingType.default = 'debit'
        subtitle_type = T("Expense")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Add %s item") % subtitle_type
    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()


    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_cashbooks_additional_items,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def additional_item_edit():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    acaiID = request.vars['acaiID']

    date = session.finance_cashbook_date

    item = db.accounting_cashbooks_additional_items(acaiID)

    booking_type = item.BookingType
    if booking_type == 'credit':
        subtitle_type = T("Income")
    elif booking_type == 'debit':
        subtitle_type = T("Expense")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Edit %s item") % subtitle_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_cashbooks_additional_items,
        return_url,
        acaiID,
        message_record_updated=T("Saved"),
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'accounting_cashbooks_additional_items'))
def additional_item_delete():
    """
    Delete cashbook item
    :return:
    """
    acaiID = request.vars['acaiID']

    query = (db.accounting_cashbooks_additional_items.id == acaiID)
    db(query).delete()

    redirect(index_return_url())


def cash_count_get(date, count_type):
    """

    :param date: datetime.date
    :param count_type: 'opening' or 'closing'
    :return:
    """
    # link_opening=URL('cash_count_add')
    # opening_balance = 0
    # info = SPAN()
    #
    # row = db.accounting_cashbooks_cash_count(
    #     BalanceCount = session.finance_cashbook_date,
    #     BalanceType = 'opening'
    # )
    #
    # if row:
    #     note = row.Note
    #     link_opening=URL('opening_balance_edit', vars={'acbID': row.id})
    #     opening_balance = row.Amount
    #
    #     au = db.auth_user(row.auth_user_id)
    #     info = SPAN(
    #         T("Opening balance set by"), ' ',
    #         A(au.display_name,
    #           _href=URL('customers', 'edit', args=[au.id])), ' ',
    #         # T("@"), ' ',
    #         # row.CreatedOn.strftime(DATETIME_FORMAT),
    #         XML(' &bull; '),
    #         _class="text-muted"
    #     )
    #
    # link_set_opening_balance = A(
    #     T("Set opening balance"),
    #     _href=link_opening,
    # )
    # info.append(link_set_opening_balance)
    from general_helpers import max_string_length

    if count_type == 'opening':
        box_class = 'box-success'
        box_title = T("Cash count opening")
        msg_not_set = T("Opening balance not set")
    elif count_type == 'closing':
        box_class = 'box-danger'
        box_title = T("Cash count closing")
        msg_not_set = T("closing balance not set")

    row = db.accounting_cashbooks_cash_count(
        CountDate = session.finance_cashbook_date,
        CountType = count_type
    )
    if row:
        total = row.Amount
        au = db.auth_user(row.auth_user_id)
        header = THEAD(TR(
            TH(T("Set by")),
            TH(T("Amount")),
        ))

        box_body = DIV(TABLE(
            header,
            TR(TD(A(au.display_name,
                    _href=URL('customers', 'edit', args=[au.id]))),
               TH(represent_float_as_amount(total))),
            _class='table table-striped table-hover'
            ),
        _class='box-body no-padding')
    else:
        total = 0
        box_body = DIV(msg_not_set, _class='box-body')


    link = ''
    link_vars = {'count_type': count_type}
    if not row:
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('create', 'accounting_cashbooks_cash_count')
        link_url = 'cash_count_add'
    else:
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('update', 'accounting_cashbooks_cash_count')
        link_url = 'cash_count_edit'
        link_vars['ccID'] = row.id

    if permission:
        link = SPAN(
            SPAN(XML(" &bull; "), _class='text-muted'),
            A(T("Set balance"),
              _href=URL(link_url, vars=link_vars))
        )

    box = DIV(
        DIV(H3(box_title, _class='box-title'),
            link,
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        box_body,
        _class='box ' + box_class,
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_classes(date, list_type='balance'):
    """
    return a box and total of class profit or class revenue
    :param list_type: one of 'revenue' or 'teacher_payments'
    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()
    revenue = reports.get_classes_revenue_summary_day(session.finance_cashbook_date)

    if list_type == 'balance':
        total = revenue['revenue_total']
        box_title = T("Class balance")
    elif list_type == 'teacher_payments':
        total = revenue['teacher_payments']
        box_title = T("Teacher payments")

    header = THEAD(TR(
        TH(T("Time")),
        TH(T("Location")),
        TH(T("Classtype")),
        TH(T("Amount")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for cls in revenue['data']:
        if list_type == 'balance':
            amount = cls['Balance']
        elif list_type == 'teacher_payments':
            amount = cls['TeacherPayment']

        tr = TR(
            TD(cls['Starttime']),
            TD(max_string_length(cls['Location'], 18)),
            TD(max_string_length(cls['ClassType'], 18)),
            TD(represent_float_as_amount(amount))
        )

        table.append(tr)

    # Footer total
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T('Total')),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(box_title, _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_classcards(date):
    """

    :param date: datetime.date
    :return:
    """
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.customers_classcards.id.count()
    rows = reports.classcards_sold_summary_rows(date, date)

    header = THEAD(TR(
        TH(T("Card")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        cards_sold = row[count]
        row_total = row.school_classcards.Price * cards_sold

        table.append(TR(
            TD(row.school_classcards.Name),
            TD(cards_sold),
            TD(represent_float_as_amount(row.school_classcards.Price)),
            TD(represent_float_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Cards"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_memberships(date):
    """

    :param date: datetime.date
    :return:
    """
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_memberships.id.count()
    rows = reports.memberships_sold_summary_rows(date, date)

    header = THEAD(TR(
        TH(T("Membership")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        cards_sold = row[count]
        row_total = row.school_memberships.Price * cards_sold

        table.append(TR(
            TD(row.school_memberships.Name),
            TD(cards_sold),
            TD(represent_float_as_amount(row.school_memberships.Price)),
            TD(represent_float_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Memberships"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_sales_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.shop_sales_products_variants.shop_products_variants_id.count()
    rows = reports.shop_sales_summary(date, date)

    header = THEAD(TR(
        TH(T("Product")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        products_sold = row[count]
        row_total = row.shop_products_variants.Price * products_sold

        table.append(TR(
            TD(max_string_length(row.shop_sales.ProductName, 46), BR(),
               SPAN(max_string_length(row.shop_sales.VariantName, 46), _class="text-muted")),
            TD(products_sold),
            TD(represent_float_as_amount(row.shop_products_variants.Price)),
            TD(represent_float_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Shop sales"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_credit_classcards_used_classes_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_classcards.id.count()
    rows = reports.classes_attendance_classcards_quickstats_summary(date, date)

    header = THEAD(TR(
        TH(T("Card")),
        TH(T("Classes taken")),
        TH(T("Class price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        classes_taken = row[count]
        class_price = row.school_classcards.Price / row.school_classcards.Classes
        row_total = class_price * classes_taken

        table.append(TR(
            TD(max_string_length(row.school_classcards.Name, 46)),
            TD(classes_taken),
            TD(represent_float_as_amount(class_price)),
            TD(represent_float_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Classes taken using cards"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger',
    )

    return dict(
        box = box,
        total = total
    )