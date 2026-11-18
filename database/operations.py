from database.database import get_connection


# --------------------------------------------------
# INVENTORY OPERATIONS
# --------------------------------------------------

def add_inventory_item(
    product_name,
    barcode=None,
    category=None,
    quantity=1,
    unit=None,
    purchase_date=None,
    expiration_date=None,
    date_confirmed=0
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO inventory_items (
                product_name,
                barcode,
                category,
                quantity,
                unit,
                purchase_date,
                expiration_date,
                date_confirmed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_name,
                barcode,
                category,
                quantity,
                unit,
                purchase_date,
                expiration_date,
                date_confirmed
            )
        )

        item_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO inventory_events (item_id, action)
            VALUES (?, 'created')
            """,
            (item_id,)
        )

        return item_id


def get_inventory():
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT *
            FROM inventory_items
            ORDER BY expiration_date ASC
            """
        )

        return cursor.fetchall()


def change_quantity(item_id, quantity_change):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE inventory_items
            SET quantity = quantity + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE item_id = ?
              AND quantity + ? >= 0
            """,
            (quantity_change, item_id, quantity_change)
        )

        if cursor.rowcount == 0:
            return False

        connection.execute(
            """
            INSERT INTO inventory_events (
                item_id,
                action,
                quantity_changed
            )
            VALUES (?, 'quantity_updated', ?)
            """,
            (item_id, quantity_change)
        )

        return True


def update_expiration_date(item_id, new_date, date_confirmed=1):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE inventory_items
            SET expiration_date = ?,
                date_confirmed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE item_id = ?
            """,
            (new_date, date_confirmed, item_id)
        )

        if cursor.rowcount == 0:
            return False

        connection.execute(
            """
            INSERT INTO inventory_events (item_id, action)
            VALUES (?, 'date_updated')
            """,
            (item_id,)
        )

        return True


def delete_inventory_item(item_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT item_id
            FROM inventory_items
            WHERE item_id = ?
            """,
            (item_id,)
        )

        if cursor.fetchone() is None:
            return False

        connection.execute(
            """
            INSERT INTO inventory_events (item_id, action)
            VALUES (?, 'deleted')
            """,
            (item_id,)
        )

        connection.execute(
            """
            DELETE FROM inventory_items
            WHERE item_id = ?
            """,
            (item_id,)
        )

        return True


# --------------------------------------------------
# SCAN CANDIDATE OPERATIONS
# --------------------------------------------------

def create_scan_candidate(
    raw_ocr_text,
    product_name=None,
    barcode=None,
    image_path=None,
    candidate_date=None,
    confidence=None
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO scan_candidates (
                product_name,
                barcode,
                image_path,
                raw_ocr_text,
                candidate_date,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product_name,
                barcode,
                image_path,
                raw_ocr_text,
                candidate_date,
                confidence
            )
        )

        return cursor.lastrowid


def get_pending_scan_candidates():
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT *
            FROM scan_candidates
            WHERE status = 'pending'
            ORDER BY created_at ASC
            """
        )

        return cursor.fetchall()


def accept_scan_candidate(
    scan_id,
    product_name=None,
    expiration_date=None,
    category=None,
    quantity=1,
    unit=None
):
    with get_connection() as connection:

        # Find the pending scan
        cursor = connection.execute(
            """
            SELECT *
            FROM scan_candidates
            WHERE scan_id = ?
              AND status = 'pending'
            """,
            (scan_id,)
        )

        scan = cursor.fetchone()

        if scan is None:
            return False

        # Use corrected values if provided
        final_name = product_name or scan["product_name"]
        final_date = expiration_date or scan["candidate_date"]

        if not final_name:
            return False

        # Create inventory item
        cursor = connection.execute(
            """
            INSERT INTO inventory_items (
                product_name,
                barcode,
                category,
                quantity,
                unit,
                expiration_date,
                date_confirmed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                final_name,
                scan["barcode"],
                category,
                quantity,
                unit,
                final_date,
                1 if final_date else 0
            )
        )

        item_id = cursor.lastrowid

        # Record inventory creation event
        connection.execute(
            """
            INSERT INTO inventory_events (item_id, action)
            VALUES (?, 'created')
            """,
            (item_id,)
        )

        # Mark scan as accepted
        connection.execute(
            """
            UPDATE scan_candidates
            SET status = 'accepted'
            WHERE scan_id = ?
            """,
            (scan_id,)
        )

        return item_id


def reject_scan_candidate(scan_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE scan_candidates
            SET status = 'rejected'
            WHERE scan_id = ?
              AND status = 'pending'
            """,
            (scan_id,)
        )

        return cursor.rowcount > 0