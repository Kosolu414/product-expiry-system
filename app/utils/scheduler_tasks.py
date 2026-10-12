from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from app.models import db, Product, AlertLog, User


def check_expiring_products_job(app, mail):
    """
    Automated background job:
    1. Scans for products expiring within 30 days or already expired.
    2. Updates status in the database.
    3. Prevents duplicate spam by checking AlertLog records sent today.
    4. Dispatches HTML summary emails to Admin & Manager users.
    """
    with app.app_context():
        today = datetime.utcnow().date()
        warning_threshold = today + timedelta(days=30)

        # Query products expiring within 30 days or already expired
        critical_products = Product.query.filter(Product.expiry_date <= warning_threshold).all()

        if not critical_products:
            print(f"[{datetime.now()}] Daily Expiry Check: No expiring products found.")
            return

        products_to_alert = []

        for product in critical_products:
            # Update product status
            old_status = product.status
            product.update_status()

            # Prevent spamming: Check if an alert was already logged today for this product
            already_logged = AlertLog.query.filter(
                AlertLog.product_id == product.id,
                db.func.date(AlertLog.alert_date) == today
            ).first()

            if not already_logged:
                products_to_alert.append(product)

        db.session.commit()

        if not products_to_alert:
            print(f"[{datetime.now()}] Daily Expiry Check: Alerts already dispatched for today.")
            return

        # Fetch recipient emails (All Admins, Managers, or the configured fallback email)
        recipient_users = User.query.filter(User.role.in_(['Admin', 'Manager'])).all()
        recipient_emails = [user.email for user in recipient_users]

        fallback_email = current_app.config.get('MANAGER_ALERT_EMAIL')
        if fallback_email and fallback_email not in recipient_emails:
            recipient_emails.append(fallback_email)

        if not recipient_emails:
            print("No recipient emails configured for expiry alerts.")
            return

        # Compose HTML Email Body
        email_body = """
        <h2>⚠️ Product Expiry Warning Report</h2>
        <p>The following items require immediate inventory action:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>Product Name</th>
                <th>Batch Number</th>
                <th>Quantity</th>
                <th>Expiry Date</th>
                <th>Status</th>
            </tr>
        """

        for prod in products_to_alert:
            status_color = "#d9534f" if prod.status == "Expired" else "#f0ad4e"
            email_body += f"""
            <tr>
                <td><b>{prod.product_name}</b></td>
                <td>{prod.batch_number}</td>
                <td>{prod.quantity}</td>
                <td>{prod.expiry_date.strftime('%Y-%m-%d')}</td>
                <td style="color: {status_color}; font-weight: bold;">{prod.status}</td>
            </tr>
            """

        email_body += """
        </table>
        <br>
        <p>Please log in to the Product Expiry Management System to manage or discount these items.</p>
        """

        try:
            msg = Message(
                subject=f"🚨 Inventory Expiry Alert ({len(products_to_alert)} Items Need Attention)",
                recipients=recipient_emails,
                html=email_body
            )
            mail.send(msg)

            # Log successfully sent alerts in DB
            for prod in products_to_alert:
                for email in recipient_emails:
                    alert_entry = AlertLog(
                        product_id=prod.id,
                        recipient_email=email,
                        alert_type=f"Expiry Warning ({prod.status})",
                        status_sent=True
                    )
                    db.session.add(alert_entry)

            db.session.commit()
            print(f"[{datetime.now()}] Expiry alert email sent successfully to {recipient_emails}")

        except Exception as e:
            print(f"Failed to send email alerts: {str(e)}")