-- ===============================
-- Antares Project - Secure SQL Dump
-- ===============================


-- Crear base de datos
CREATE DATABASE IF NOT EXISTS ddbb_antares_project;
USE ddbb_antares_project;

-- ===============================
-- Tabla de Usuarios
-- ===============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'tutor', 'alumno') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===============================
-- Tabla de Cursos
-- ===============================
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL,
    tutor_id INT NOT NULL,
    admin_id INT,
    status ENUM('borrador', 'publicado') DEFAULT 'borrador',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tutor_id) REFERENCES users(id),
    FOREIGN KEY (admin_id) REFERENCES users(id),
    CONSTRAINT chk_price_positive CHECK (price > 0),
    CONSTRAINT chk_duration_positive CHECK (duration > 0)
);


CREATE TABLE course_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    file_type ENUM('video', 'pdf', 'image', 'texto') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);



CREATE TABLE materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    file_name VARCHAR(255),
    file_path TEXT,
    file_type VARCHAR(50),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);



-- file_type: Tipo del archivo para distinguir video, pdf, imagen o texto.

-- file_path: Ruta relativa o URL del archivo almacenado en el servidor o almacenamiento.

-- uploaded_at: Fecha de subida para auditoría.



-- ===============================
-- Tabla de Relación Alumno-Curso
-- ===============================
CREATE TABLE student_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    payment_status ENUM('pendiente', 'verificado') DEFAULT 'pendiente',
    payment_date TIMESTAMP NULL,
    payment_receipt_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- ===============================
-- Tabla de Pagos
-- ===============================
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('tarjeta', 'paypal', 'transferencia'),
    receipt_url VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    CONSTRAINT chk_amount_positive CHECK (amount > 0)
);




-- ===============================
-- Tabla de Mensajes
-- ===============================
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    subject VARCHAR(100),
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);


CREATE TABLE certificados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    certificate_code VARCHAR(50) UNIQUE NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    CONSTRAINT chk_certificate_unique UNIQUE(student_id, course_id)  -- Un certificado único por alumno y curso
);



CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),  -- Calificación de 1 a 5
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    CONSTRAINT chk_review_unique UNIQUE(student_id, course_id)  -- Un alumno puede dejar solo una reseña por curso
);




-- ===============================
-- Tabla de Historial de Pagos
-- ===============================
CREATE TABLE payment_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    old_status ENUM('pendiente', 'verificado') NOT NULL,
    new_status ENUM('pendiente', 'verificado') NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by INT NOT NULL,  -- Administrador que hizo el cambio
    FOREIGN KEY (payment_id) REFERENCES payments(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);


-- ===============================
-- Tabla de Auditoría
-- ===============================
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_data TEXT,
    new_data TEXT,
    changed_by INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS sync_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- ===============================
-- VIEWS Por Rol
-- ===============================


-- ===============================
-- Vista para reseñas no verificadas
-- ===============================
CREATE VIEW view_unverified_reviews AS
SELECT r.id AS review_id, 
       u.full_name AS student_name, 
       c.title AS course_title, 
       r.rating, 
       r.comment, 
       r.created_at
FROM reviews r
JOIN users u ON r.student_id = u.id
JOIN courses c ON r.course_id = c.id
WHERE r.verified = FALSE;





-- ===============================
-- Vista para Historial de Pagos
-- ===============================
CREATE VIEW view_payment_history AS
SELECT p.id AS payment_id, 
       ph.old_status, 
       ph.new_status, 
       ph.changed_at, 
       u.full_name AS changed_by
FROM payment_history ph
JOIN payments p ON ph.payment_id = p.id
JOIN users u ON ph.changed_by = u.id;





-- Vista para tutores
CREATE VIEW view_tutor_courses AS
SELECT c.*, u.full_name AS tutor_name
FROM courses c
JOIN users u ON c.tutor_id = u.id
WHERE u.role = 'tutor';

-- Vista para alumnos: cursos en los que está inscrito
CREATE VIEW view_alumno_courses AS
SELECT sc.*, c.title, c.description, c.duration, c.price
FROM student_courses sc
JOIN courses c ON sc.course_id = c.id
JOIN users u ON sc.student_id = u.id
WHERE u.role = 'alumno';

-- Vista para administradores: listado completo de cursos
CREATE VIEW view_admin_courses AS
SELECT c.*, 
       tu.full_name AS tutor_name,
       ad.full_name AS admin_name
FROM courses c
LEFT JOIN users tu ON c.tutor_id = tu.id
LEFT JOIN users ad ON c.admin_id = ad.id;



-- Vista para administradores: todos los certificados emitidos
CREATE VIEW view_certificados AS
SELECT c.title AS course_title, u.full_name AS student_name, ce.certificate_code, ce.issued_at
FROM certificados ce
JOIN users u ON ce.student_id = u.id
JOIN courses c ON ce.course_id = c.id;


-- Vista para administradores: todas las reseñas de los cursos
CREATE VIEW view_reviews AS
SELECT c.title AS course_title, u.full_name AS student_name, r.rating, r.comment, r.created_at
FROM reviews r
JOIN users u ON r.student_id = u.id
JOIN courses c ON r.course_id = c.id;


-- Vista para administradores: pagos verificados
CREATE VIEW view_verified_payments AS
SELECT p.amount, p.payment_method, p.payment_date, sc.payment_status, u.full_name AS student_name, c.title AS course_title
FROM payments p
JOIN student_courses sc ON p.student_id = sc.student_id AND p.course_id = sc.course_id
JOIN users u ON p.student_id = u.id
JOIN courses c ON p.course_id = c.id
WHERE p.verified = TRUE;



CREATE VIEW view_inbox_messages AS
SELECT m.id, 
       u1.full_name AS sender_name, 
       u2.full_name AS receiver_name, 
       m.subject, m.body, 
       m.sent_at, m.read_at
FROM messages m
JOIN users u1 ON m.sender_id = u1.id
JOIN users u2 ON m.receiver_id = u2.id;



CREATE VIEW view_certificates_by_user AS
SELECT u.full_name AS student_name, c.title AS course_title, ce.certificate_code, ce.issued_at
FROM certificados ce
JOIN users u ON ce.student_id = u.id
JOIN courses c ON ce.course_id = c.id;




-- ===============================
-- STORED PROCEDURES
-- ===============================



DELIMITER $$

CREATE PROCEDURE sp_create_course (
    IN p_tutor_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT
)
BEGIN
    INSERT INTO courses (tutor_id, title, description, status)
    VALUES (p_tutor_id, p_title, p_description, 'pendiente');
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE sp_add_course_file (
    IN p_course_id INT,
    IN p_file_type ENUM('video', 'pdf', 'image', 'texto'),
    IN p_file_path VARCHAR(500)
)
BEGIN
    INSERT INTO course_files (course_id, file_type, file_path)
    VALUES (p_course_id, p_file_type, p_file_path);
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE sp_get_tutor_courses (
    IN p_tutor_id INT
)
BEGIN
    SELECT * FROM courses WHERE tutor_id = p_tutor_id;
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE sp_get_course_files (
    IN p_course_id INT
)
BEGIN
    SELECT file_type, file_path, uploaded_at
    FROM course_files
    WHERE course_id = p_course_id;
END $$

DELIMITER ;



DELIMITER $$

CREATE PROCEDURE sp_approve_course (
    IN p_course_id INT
)
BEGIN
    UPDATE courses SET status = 'aprobado'
    WHERE id = p_course_id;
END $$

DELIMITER ;



DELIMITER $$

-- Registrar cambios en la auditoría
CREATE PROCEDURE sp_audit_change (
    IN p_table_name VARCHAR(100),
    IN p_record_id INT,
    IN p_action ENUM('INSERT', 'UPDATE', 'DELETE'),
    IN p_old_data TEXT,
    IN p_new_data TEXT,
    IN p_user_id INT
)
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, changed_by)
    VALUES (p_table_name, p_record_id, p_action, p_old_data, p_new_data, p_user_id);
END $$

DELIMITER ;




DELIMITER $$

-- Verificar reseña (solo admin)
CREATE PROCEDURE sp_verify_review (
    IN p_review_id INT,
    IN p_admin_id INT
)
BEGIN
    DECLARE admin_role ENUM('admin', 'tutor', 'alumno');

    -- Verificar que el usuario sea administrador
    SELECT role INTO admin_role FROM users WHERE id = p_admin_id;

    IF admin_role = 'admin' THEN
        -- Actualizar la reseña a verificada
        UPDATE reviews 
        SET verified = TRUE 
        WHERE id = p_review_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No autorizado para verificar reseñas.';
    END IF;
END $$

DELIMITER ;





DELIMITER $$

-- Registrar cambio en el historial de pagos
CREATE PROCEDURE sp_record_payment_history (
    IN p_payment_id INT,
    IN p_old_status ENUM('pendiente', 'verificado'),
    IN p_new_status ENUM('pendiente', 'verificado'),
    IN p_admin_id INT
)
BEGIN
    -- Insertar el cambio de estado en el historial
    INSERT INTO payment_history (payment_id, old_status, new_status, changed_by)
    VALUES (p_payment_id, p_old_status, p_new_status, p_admin_id);
END $$

DELIMITER ;




DELIMITER $$

-- Emitir certificado (solo si el pago está verificado y el curso está completado)
CREATE PROCEDURE sp_issue_certificate (
    IN p_student_id INT,
    IN p_course_id INT
)
BEGIN
    DECLARE payment_status ENUM('pendiente', 'verificado');
    DECLARE course_status ENUM('borrador', 'publicado');
    
    -- Verificar el estado del pago
    SELECT sc.payment_status INTO payment_status
    FROM student_courses sc
    WHERE sc.student_id = p_student_id AND sc.course_id = p_course_id;
    
    -- Verificar si el curso está publicado
    SELECT c.status INTO course_status
    FROM courses c
    WHERE c.id = p_course_id;
    
    -- Solo emitir certificado si el pago está verificado y el curso está publicado
    IF payment_status = 'verificado' AND course_status = 'publicado' THEN
        INSERT INTO certificados (student_id, course_id, certificate_code)
        VALUES (p_student_id, p_course_id, CONCAT('CERT-', UUID()));
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede emitir el certificado. El pago debe estar verificado y el curso debe estar publicado.';
    END IF;
END $$

DELIMITER ;





DELIMITER $$

-- Registrar nuevo curso (solo si es tutor)
CREATE PROCEDURE sp_create_course (
    IN p_title VARCHAR(100),
    IN p_description TEXT,
    IN p_price DECIMAL(10,2),
    IN p_duration INT,
    IN p_tutor_id INT
)
BEGIN
    DECLARE tutor_role ENUM('admin', 'tutor', 'alumno');

    SELECT role INTO tutor_role FROM users WHERE id = p_tutor_id;

    IF tutor_role = 'tutor' THEN
        INSERT INTO courses (title, description, price, duration, tutor_id)
        VALUES (p_title, p_description, p_price, p_duration, p_tutor_id);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo los tutores
         pueden crear cursos.';
    END IF;
END $$

-- Verificar pago manualmente (solo admin)
CREATE PROCEDURE sp_verify_payment (
    IN p_payment_id INT,
    IN p_admin_id INT
)
BEGIN
    DECLARE admin_role ENUM('admin', 'tutor', 'alumno');

    SELECT role INTO admin_role FROM users WHERE id = p_admin_id;

    IF admin_role = 'admin' THEN
        UPDATE payments
        SET verified = TRUE
        WHERE id = p_payment_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No autorizado
         para verificar pagos.';
    END IF;
END $$

DELIMITER ;



DELIMITER $$

-- Verificar reseña (solo si es admin)
CREATE PROCEDURE sp_verify_review (
    IN p_review_id INT,
    IN p_admin_id INT
)
BEGIN
    DECLARE admin_role ENUM('admin', 'tutor', 'alumno');

    -- Verificar que el usuario sea administrador
    SELECT role INTO admin_role FROM users WHERE id = p_admin_id;

    IF admin_role = 'admin' THEN
        -- Aquí podrías agregar más lógica para moderar reseñas si fuera necesario (por ejemplo, si contiene lenguaje inapropiado)
        UPDATE reviews SET verified = TRUE WHERE id = p_review_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No autorizado para verificar reseñas.';
    END IF;
END $$

DELIMITER ;




-- ===============================
-- TRIGGERS
-- ===============================

DELIMITER $$

CREATE TRIGGER trg_sync_courses
AFTER INSERT OR UPDATE OR DELETE ON courses
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;

    IF (NEW.id IS NOT NULL) THEN
        SET affected_id = NEW.id;
    ELSE
        SET affected_id = OLD.id;
    END IF;

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'courses',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER trg_sync_users
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;

    IF (NEW.id IS NOT NULL) THEN
        SET affected_id = NEW.id;
    ELSE
        SET affected_id = OLD.id;
    END IF;

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'users',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_sync_courses
AFTER INSERT OR UPDATE OR DELETE ON courses
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;

    IF (NEW.id IS NOT NULL) THEN
        SET affected_id = NEW.id;
    ELSE
        SET affected_id = OLD.id;
    END IF;

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'courses',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;




DELIMITER $$

CREATE TRIGGER trg_sync_payments
AFTER INSERT OR UPDATE OR DELETE ON payments
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;

    IF (NEW.id IS NOT NULL) THEN
        SET affected_id = NEW.id;
    ELSE
        SET affected_id = OLD.id;
    END IF;

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'payments',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_sync_reviews
AFTER INSERT OR UPDATE OR DELETE ON reviews
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;

    IF (NEW.id IS NOT NULL) THEN
        SET affected_id = NEW.id;
    ELSE
        SET affected_id = OLD.id;
    END IF;

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'reviews',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_sync_messages
AFTER INSERT OR UPDATE OR DELETE ON messages
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;
    SET affected_id = IFNULL(NEW.id, OLD.id);

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'messages',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_sync_student_courses
AFTER INSERT OR UPDATE OR DELETE ON student_courses
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;
    SET affected_id = IFNULL(NEW.id, OLD.id);

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'student_courses',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;





DELIMITER $$

CREATE TRIGGER trg_sync_certificados
AFTER INSERT OR UPDATE OR DELETE ON certificados
FOR EACH ROW
BEGIN
    DECLARE affected_id INT;
    SET affected_id = IFNULL(NEW.id, OLD.id);

    INSERT INTO sync_queue (table_name, record_id, action)
    VALUES (
        'certificados',
        affected_id,
        CASE
            WHEN NEW.id IS NOT NULL AND OLD.id IS NULL THEN 'INSERT'
            WHEN NEW.id IS NOT NULL AND OLD.id IS NOT NULL THEN 'UPDATE'
            WHEN NEW.id IS NULL AND OLD.id IS NOT NULL THEN 'DELETE'
        END
    );
END$$

DELIMITER ;



DELIMITER $$

CREATE PROCEDURE sp_send_message (
    IN p_sender_id INT,
    IN p_receiver_id INT,
    IN p_subject VARCHAR(100),
    IN p_body TEXT
)
BEGIN
    DECLARE sender_role ENUM('admin', 'tutor', 'alumno');

    -- Opcional: verificar rol
    SELECT role INTO sender_role FROM users WHERE id = p_sender_id;

    IF sender_role IS NOT NULL THEN
        INSERT INTO messages (sender_id, receiver_id, subject, body)
        VALUES (p_sender_id, p_receiver_id, p_subject, p_body);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Remitente inválido.';
    END IF;
END$$

DELIMITER ;




DELIMITER $$

-- Registrar cambios en la tabla courses
CREATE TRIGGER trg_audit_course_change
AFTER INSERT OR UPDATE OR DELETE ON courses
FOR EACH ROW
BEGIN
    DECLARE old_data TEXT;
    DECLARE new_data TEXT;
    
    -- Para INSERT: Solo hay nuevos datos
    IF (NEW.id IS NOT NULL AND OLD.id IS NULL) THEN
        SET new_data = CONCAT('title: ', NEW.title, ', description: ', NEW.description, ', price: ', NEW.price);
        CALL sp_audit_change('courses', NEW.id, 'INSERT', NULL, new_data, NEW.tutor_id);
    END IF;
    
    -- Para UPDATE: Registro de los datos antiguos y nuevos
    IF (NEW.id IS NOT NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('title: ', OLD.title, ', description: ', OLD.description, ', price: ', OLD.price);
        SET new_data = CONCAT('title: ', NEW.title, ', description: ', NEW.description, ', price: ', NEW.price);
        CALL sp_audit_change('courses', NEW.id, 'UPDATE', old_data, new_data, NEW.tutor_id);
    END IF;
    
    -- Para DELETE: Solo se registra los datos antiguos
    IF (NEW.id IS NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('title: ', OLD.title, ', description: ', OLD.description, ', price: ', OLD.price);
        CALL sp_audit_change('courses', OLD.id, 'DELETE', old_data, NULL, OLD.tutor_id);
    END IF;
END $$

DELIMITER ;





DELIMITER $$

-- Registrar cambios en la tabla reviews
CREATE TRIGGER trg_audit_review_change
AFTER INSERT OR UPDATE OR DELETE ON reviews
FOR EACH ROW
BEGIN
    DECLARE old_data TEXT;
    DECLARE new_data TEXT;
    
    -- Para INSERT: Solo hay nuevos datos
    IF (NEW.id IS NOT NULL AND OLD.id IS NULL) THEN
        SET new_data = CONCAT('rating: ', NEW.rating, ', comment: ', NEW.comment, ', verified: ', NEW.verified);
        CALL sp_audit_change('reviews', NEW.id, 'INSERT', NULL, new_data, NEW.student_id);
    END IF;
    
    -- Para UPDATE: Registro de los datos antiguos y nuevos
    IF (NEW.id IS NOT NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('rating: ', OLD.rating, ', comment: ', OLD.comment, ', verified: ', OLD.verified);
        SET new_data = CONCAT('rating: ', NEW.rating, ', comment: ', NEW.comment, ', verified: ', NEW.verified);
        CALL sp_audit_change('reviews', NEW.id, 'UPDATE', old_data, new_data, NEW.student_id);
    END IF;
    
    -- Para DELETE: Solo se registra los datos antiguos
    IF (NEW.id IS NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('rating: ', OLD.rating, ', comment: ', OLD.comment, ', verified: ', OLD.verified);
        CALL sp_audit_change('reviews', OLD.id, 'DELETE', old_data, NULL, OLD.student_id);
    END IF;
END $$

DELIMITER ;






DELIMITER $$

-- Registrar cambios en la tabla payments
CREATE TRIGGER trg_audit_payment_change
AFTER INSERT OR UPDATE OR DELETE ON payments
FOR EACH ROW
BEGIN
    DECLARE old_data TEXT;
    DECLARE new_data TEXT;
    
    -- Para INSERT: Solo hay nuevos datos
    IF (NEW.id IS NOT NULL AND OLD.id IS NULL) THEN
        SET new_data = CONCAT('amount: ', NEW.amount, ', method: ', NEW.payment_method, ', verified: ', NEW.verified);
        CALL sp_audit_change('payments', NEW.id, 'INSERT', NULL, new_data, NEW.student_id);
    END IF;
    
    -- Para UPDATE: Registro de los datos antiguos y nuevos
    IF (NEW.id IS NOT NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('amount: ', OLD.amount, ', method: ', OLD.payment_method, ', verified: ', OLD.verified);
        SET new_data = CONCAT('amount: ', NEW.amount, ', method: ', NEW.payment_method, ', verified: ', NEW.verified);
        CALL sp_audit_change('payments', NEW.id, 'UPDATE', old_data, new_data, NEW.student_id);
    END IF;
    
    -- Para DELETE: Solo se registra los datos antiguos
    IF (NEW.id IS NULL AND OLD.id IS NOT NULL) THEN
        SET old_data = CONCAT('amount: ', OLD.amount, ', method: ', OLD.payment_method, ', verified: ', OLD.verified);
        CALL sp_audit_change('payments', OLD.id, 'DELETE', old_data, NULL, OLD.student_id);
    END IF;
END $$

DELIMITER ;





DELIMITER $$

-- Actualizar estado del curso cuando se verifica una reseña
CREATE TRIGGER trg_update_course_status_on_review_verification
AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    -- Verificar si la reseña fue verificada
    IF NEW.verified = TRUE THEN
        -- Actualizar el estado del curso a "con reseñas"
        UPDATE courses
        SET status = 'con reseñas'
        WHERE id = NEW.course_id;
    END IF;
END $$

DELIMITER ;





DELIMITER $$

-- Registrar automáticamente en el historial cuando el estado del pago cambie
CREATE TRIGGER trg_record_payment_status_change
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    -- Solo registrar si el estado ha cambiado
    IF OLD.verified != NEW.verified THEN
        -- Llamar al procedimiento para registrar el cambio
        CALL sp_record_payment_history(NEW.id, 
                                        IFNULL(OLD.verified, 'pendiente'), 
                                        IFNULL(NEW.verified, 'pendiente'),
                                        NEW.student_id);  -- Asumimos que el admin realiza el cambio
    END IF;
END $$

DELIMITER ;






DELIMITER $$

-- Emitir certificado automáticamente cuando el pago se verifique
CREATE TRIGGER trg_issue_certificate
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    -- Verificar si el pago ha sido verificado
    IF NEW.verified = TRUE THEN
        -- Llamar al procedimiento para emitir certificado
        CALL sp_issue_certificate(NEW.student_id, NEW.course_id);
    END IF;
END $$

DELIMITER ;



DELIMITER $$

-- Actualizar estado del curso cuando se deja una reseña
CREATE TRIGGER trg_update_course_status_on_review
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE courses
    SET status = 'con reseñas'
    WHERE id = NEW.course_id;
END $$

DELIMITER ;




DELIMITER $$

-- Sincroniza automáticamente estado del curso del alumno al pagar
CREATE TRIGGER trg_verify_payment
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    UPDATE student_courses
    SET payment_status = 'verificado',
        payment_date = NEW.created_at,
        payment_receipt_url = NEW.receipt_url
    WHERE student_id = NEW.student_id AND course_id = NEW.course_id;
END$$

DELIMITER ;

-- ===============================
-- FIN DE ARCHIVO
-- ===============================
