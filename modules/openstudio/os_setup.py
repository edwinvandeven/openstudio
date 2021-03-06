# -*- coding: utf-8 -*-

from gluon import *

class OsSetup:
    def __init__(self):
        self.set_sys_property = current.globalenv['set_sys_property']

    def setup(self):
        """
        Run setup
        :return:
        """
        self._setup_system_worksflow()
        self._setup_shop_subscriptions_payment_method()
        self._setup_sys_notifications()
        self._setup_teachers_payment_rate_type()


    def _setup_system_worksflow(self):
        self.set_sys_property(
            'system_enable_class_checkin_trialclass',
            'on'
        )


    def _setup_shop_subscriptions_payment_method(self):
        """
        Set shop subscriptions payment method to mollie by default
        """
        self.set_sys_property(
            'shop_subscriptions_payment_method',
            'mollie'
        )


    def _setup_sys_notifications(self):
        """
        Populate db.sys_notifications with default values
        """
        T = current.T
        db = current.db

        db.sys_notifications.insert(
            Notification="order_created",
            NotificationTitle=T("New order"),
            NotificationTemplate="{order_items}"
        )


    def _setup_teachers_payment_rate_type(self):
        """
        Set teacher payment rate type to 'fixed rate' by default
        """
        self.set_sys_property(
            'TeacherPaymentRateType',
            'fixed'
        )