# =============================================================
# modules/notifications.py - Notifications & Alerts Module
# =============================================================
# Central place for farm notifications and important alerts:
#   - View notifications (role-aware)
#   - View important / emergency alerts
#   - Create notification (admin / farm owner)
# =============================================================

from datetime import datetime
from database import get_connection
from config import print_header, print_line


def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------
# Create a notification (admin / farm owner)
# ---------------------------------------------------------
def create_notification(title, message="", category="General",
                        priority="Normal", target_role="all",
                        created_by="system"):
    """Insert a notification row. Returns the new id or None."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications
                (title, message, category, priority, target_role, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, message, category, priority, target_role, created_by, get_now()))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"  [ERROR]: {e}")
        return None


# ---------------------------------------------------------
# View notifications for the current user's role
# ---------------------------------------------------------
def view_notifications(current_user: dict):
    """Show notifications targeted at the current role (or 'all')."""
    print_header("NOTIFICATIONS")

    role = current_user.get('role', 'all')
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM notifications
            WHERE target_role = 'all' OR target_role = ?
            ORDER BY created_at DESC
        """, (role,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No notifications.")
            return

        for n in rows:
            mark = "[UNREAD]" if not n['is_read'] else "        "
            print(f"  {mark} #{n['id']} {n['title']}  ({n['priority']})")
            if n['message']:
                print(f"          {n['message']}")
            print(f"          {n['category']} | {n['created_at']} | by {n['created_by']}")
            print_line("-")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# View important / emergency alerts
# ---------------------------------------------------------
def view_alerts(current_user: dict):
    """Show only Important / Emergency / Critical priority alerts."""
    print_header("IMPORTANT ALERTS")

    role = current_user.get('role', 'all')
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM notifications
            WHERE (target_role = 'all' OR target_role = ?)
              AND priority IN ('Important', 'Emergency', 'Critical')
            ORDER BY created_at DESC
        """, (role,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No important alerts right now. Farm is all clear.")
            return

        for n in rows:
            print(f"  [{'!':^1}] #{n['id']} {n['title']}  ({n['priority']})")
            if n['message']:
                print(f"          {n['message']}")
            print(f"          {n['category']} | {n['created_at']}")
            print_line("-")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Mark a notification as read
# ---------------------------------------------------------
def mark_notification_read(notification_id: int):
    """Mark a single notification as read."""
    try:
        conn = get_connection()
        conn.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass
