--
-- PostgreSQL database dump
--

\restrict wxNR4eNRqMSkNKzBwnlNdlzUjzmh0u23Cuee8BnLvs5M6LhGkFed07d2Fq4EKgW

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: _migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public._migrations (
    filename text NOT NULL,
    applied_at timestamp without time zone DEFAULT now()
);


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    staff_id integer,
    table_name character varying(100) NOT NULL,
    old_value text,
    new_value text,
    changed_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: bookings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bookings (
    id integer NOT NULL,
    guest_id integer NOT NULL,
    room_id integer NOT NULL,
    staff_id integer,
    check_in date NOT NULL,
    check_out date NOT NULL,
    total_price numeric(12,2) DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'Подтверждено'::character varying NOT NULL,
    payment_status character varying(20) DEFAULT 'Не оплачено'::character varying NOT NULL,
    yookassa_payment_id character varying(50),
    CONSTRAINT bookings_check CHECK ((check_out > check_in)),
    CONSTRAINT bookings_payment_status_check CHECK (((payment_status)::text = ANY ((ARRAY['Не оплачено'::character varying, 'Оплачено'::character varying, 'Возврат'::character varying])::text[]))),
    CONSTRAINT bookings_status_check CHECK (((status)::text = ANY ((ARRAY['Ожидает оплаты'::character varying, 'Подтверждено'::character varying, 'Ожидает возврата'::character varying, 'Отменено'::character varying, 'Завершено'::character varying])::text[])))
);


--
-- Name: bookings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bookings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;


--
-- Name: guest_pref_link; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guest_pref_link (
    guest_id integer NOT NULL,
    preference_id integer NOT NULL
);


--
-- Name: guest_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guest_preferences (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


--
-- Name: guest_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.guest_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: guest_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.guest_preferences_id_seq OWNED BY public.guest_preferences.id;


--
-- Name: guests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guests (
    id integer NOT NULL,
    full_name character varying(300) NOT NULL,
    passport character varying(100) NOT NULL,
    phone character varying(30),
    email character varying(200),
    loyalty_tier character varying(20) DEFAULT 'Silver'::character varying NOT NULL,
    total_spend numeric(12,2) DEFAULT 0 NOT NULL,
    CONSTRAINT guests_loyalty_tier_check CHECK (((loyalty_tier)::text = ANY ((ARRAY['Silver'::character varying, 'Gold'::character varying, 'Platinum'::character varying])::text[])))
);


--
-- Name: guests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.guests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: guests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.guests_id_seq OWNED BY public.guests.id;


--
-- Name: hotels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    address text NOT NULL,
    director_name character varying(200) NOT NULL,
    overbooking_limit integer DEFAULT 10 NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6)
);


--
-- Name: hotels_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hotels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hotels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hotels_id_seq OWNED BY public.hotels.id;


--
-- Name: refund_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refund_requests (
    id integer NOT NULL,
    booking_id integer,
    guest_id integer,
    amount numeric(10,2) NOT NULL,
    status character varying(20) DEFAULT 'Новая'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    resolved_at timestamp without time zone,
    manager_id integer,
    CONSTRAINT refund_requests_status_check CHECK (((status)::text = ANY ((ARRAY['Новая'::character varying, 'Одобрена'::character varying, 'Отклонена'::character varying])::text[])))
);


--
-- Name: refund_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.refund_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refund_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.refund_requests_id_seq OWNED BY public.refund_requests.id;


--
-- Name: replenishment_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.replenishment_requests (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    hotel_id integer NOT NULL,
    item_name character varying(200) NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    unit character varying(50) DEFAULT 'шт'::character varying,
    status character varying(20) DEFAULT 'Новый'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT replenishment_requests_status_check CHECK (((status)::text = ANY ((ARRAY['Новый'::character varying, 'Одобрен'::character varying, 'Отклонён'::character varying, 'Выполнен'::character varying])::text[])))
);


--
-- Name: replenishment_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.replenishment_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: replenishment_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.replenishment_requests_id_seq OWNED BY public.replenishment_requests.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    booking_id integer NOT NULL,
    guest_id integer NOT NULL,
    hotel_id integer NOT NULL,
    rating integer NOT NULL,
    comment text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: room_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.room_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    base_price numeric(10,2) NOT NULL,
    capacity integer DEFAULT 2 NOT NULL
);


--
-- Name: room_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.room_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: room_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.room_categories_id_seq OWNED BY public.room_categories.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    hotel_id integer NOT NULL,
    category_id integer NOT NULL,
    room_number integer NOT NULL,
    cleaning_status character varying(20) DEFAULT 'Clean'::character varying NOT NULL,
    room_condition character varying(20) DEFAULT 'Исправно'::character varying NOT NULL,
    CONSTRAINT rooms_cleaning_status_check CHECK (((cleaning_status)::text = ANY ((ARRAY['Clean'::character varying, 'Dirty'::character varying, 'Cleaning'::character varying])::text[]))),
    CONSTRAINT rooms_room_condition_check CHECK (((room_condition)::text = ANY ((ARRAY['Исправно'::character varying, 'Ремонт'::character varying])::text[])))
);


--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: service_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.service_orders (
    id integer NOT NULL,
    booking_id integer NOT NULL,
    service_id integer NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    ordered_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: service_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.service_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: service_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.service_orders_id_seq OWNED BY public.service_orders.id;


--
-- Name: service_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.service_requests (
    id integer NOT NULL,
    admin_id integer NOT NULL,
    manager_id integer,
    hotel_id integer NOT NULL,
    description text NOT NULL,
    status character varying(20) DEFAULT 'Новый'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT service_requests_status_check CHECK (((status)::text = ANY ((ARRAY['Новый'::character varying, 'В работе'::character varying, 'Выполнен'::character varying])::text[])))
);


--
-- Name: service_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.service_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: service_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.service_requests_id_seq OWNED BY public.service_requests.id;


--
-- Name: services; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    price numeric(10,2) NOT NULL,
    is_package boolean DEFAULT false NOT NULL
);


--
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- Name: staff; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff (
    id integer NOT NULL,
    hotel_id integer NOT NULL,
    full_name character varying(300) NOT NULL,
    role character varying(50) NOT NULL,
    login character varying(100) NOT NULL,
    password_hash character varying(200) NOT NULL,
    manager_id integer,
    CONSTRAINT staff_role_check CHECK (((role)::text = ANY ((ARRAY['Администратор'::character varying, 'Менеджер'::character varying, 'Горничная'::character varying, 'Уборщик'::character varying, 'Сантехник'::character varying, 'Бармен'::character varying, 'Техник'::character varying])::text[])))
);


--
-- Name: staff_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: staff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.staff_id_seq OWNED BY public.staff.id;


--
-- Name: staff_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff_schedules (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    work_date date NOT NULL,
    shift character varying(20) DEFAULT 'День'::character varying NOT NULL,
    note text,
    CONSTRAINT staff_schedules_shift_check CHECK (((shift)::text = ANY ((ARRAY['Утро'::character varying, 'День'::character varying, 'Вечер'::character varying, 'Ночь'::character varying])::text[])))
);


--
-- Name: staff_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.staff_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: staff_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.staff_schedules_id_seq OWNED BY public.staff_schedules.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    guest_id integer,
    login character varying(100) NOT NULL,
    password_hash character varying(200) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: bookings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);


--
-- Name: guest_preferences id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_preferences ALTER COLUMN id SET DEFAULT nextval('public.guest_preferences_id_seq'::regclass);


--
-- Name: guests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guests ALTER COLUMN id SET DEFAULT nextval('public.guests_id_seq'::regclass);


--
-- Name: hotels id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels ALTER COLUMN id SET DEFAULT nextval('public.hotels_id_seq'::regclass);


--
-- Name: refund_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refund_requests ALTER COLUMN id SET DEFAULT nextval('public.refund_requests_id_seq'::regclass);


--
-- Name: replenishment_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.replenishment_requests ALTER COLUMN id SET DEFAULT nextval('public.replenishment_requests_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: room_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room_categories ALTER COLUMN id SET DEFAULT nextval('public.room_categories_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: service_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_orders ALTER COLUMN id SET DEFAULT nextval('public.service_orders_id_seq'::regclass);


--
-- Name: service_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_requests ALTER COLUMN id SET DEFAULT nextval('public.service_requests_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- Name: staff id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff ALTER COLUMN id SET DEFAULT nextval('public.staff_id_seq'::regclass);


--
-- Name: staff_schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_schedules ALTER COLUMN id SET DEFAULT nextval('public.staff_schedules_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: _migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public._migrations (filename, applied_at) FROM stdin;
001_init.sql	2026-05-26 16:59:33.093766
002_seed.sql	2026-05-26 16:59:33.100706
003_roles_auth.sql	2026-05-26 16:59:33.122653
004_coordinates.sql	2026-05-26 16:59:33.123873
005_payment_status.sql	2026-05-26 16:59:33.124822
006_booking_status.sql	2026-05-26 16:59:33.125824
007_payment_id.sql	2026-05-26 16:59:33.126383
008_refund_requests.sql	2026-05-26 16:59:33.129413
009_refund_status.sql	2026-05-26 16:59:33.130185
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_log (id, staff_id, table_name, old_value, new_value, changed_at) FROM stdin;
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bookings (id, guest_id, room_id, staff_id, check_in, check_out, total_price, status, payment_status, yookassa_payment_id) FROM stdin;
1	1	3	1	2025-05-01	2025-05-05	32760.00	Завершено	Не оплачено	\N
2	2	1	1	2025-05-10	2025-05-12	7000.00	Завершено	Не оплачено	\N
3	3	5	1	2025-06-01	2025-06-07	122850.00	Подтверждено	Не оплачено	\N
4	4	2	1	2025-06-15	2025-06-17	9100.00	Подтверждено	Не оплачено	\N
5	5	7	4	2025-07-01	2025-07-10	49140.00	Подтверждено	Не оплачено	\N
6	6	8	4	2025-07-05	2025-07-08	13650.00	Подтверждено	Не оплачено	\N
7	7	9	4	2025-08-01	2025-08-07	55692.00	Подтверждено	Не оплачено	\N
8	8	11	6	2025-08-10	2025-08-14	18200.00	Подтверждено	Не оплачено	\N
9	9	3	1	2025-04-01	2025-04-03	11900.00	Завершено	Не оплачено	\N
10	10	1	1	2025-04-20	2025-04-22	5950.00	Завершено	Не оплачено	\N
11	1	5	1	2025-09-10	2025-09-15	75000.00	Подтверждено	Не оплачено	\N
12	3	13	6	2025-10-01	2025-10-05	60000.00	Подтверждено	Не оплачено	\N
13	1	3	1	2025-05-01	2025-05-05	32760.00	Завершено	Не оплачено	\N
14	2	1	1	2025-05-10	2025-05-12	7000.00	Завершено	Не оплачено	\N
15	3	5	1	2025-06-01	2025-06-07	122850.00	Подтверждено	Не оплачено	\N
16	4	2	1	2025-06-15	2025-06-17	9100.00	Подтверждено	Не оплачено	\N
17	5	7	4	2025-07-01	2025-07-10	49140.00	Подтверждено	Не оплачено	\N
18	6	8	4	2025-07-05	2025-07-08	13650.00	Подтверждено	Не оплачено	\N
19	7	9	4	2025-08-01	2025-08-07	55692.00	Подтверждено	Не оплачено	\N
20	8	11	6	2025-08-10	2025-08-14	18200.00	Подтверждено	Не оплачено	\N
21	9	3	1	2025-04-01	2025-04-03	11900.00	Завершено	Не оплачено	\N
22	10	1	1	2025-04-20	2025-04-22	5950.00	Завершено	Не оплачено	\N
23	1	5	1	2025-09-10	2025-09-15	75000.00	Подтверждено	Не оплачено	\N
24	3	13	6	2025-10-01	2025-10-05	60000.00	Подтверждено	Не оплачено	\N
25	1	1	\N	2026-05-27	2026-05-29	6300.00	Подтверждено	Оплачено	mock-19ea52d4-c093-48a3-83c7-0e423aeb51f6
26	1	5	\N	2026-05-28	2026-05-29	13500.00	Подтверждено	Оплачено	mock-44379fd2-1d4c-45e3-8322-7f9d2162682d
\.


--
-- Data for Name: guest_pref_link; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.guest_pref_link (guest_id, preference_id) FROM stdin;
1	2
1	4
2	1
3	3
3	2
4	5
5	4
7	1
7	6
\.


--
-- Data for Name: guest_preferences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.guest_preferences (id, name) FROM stdin;
1	Без ковролина
2	Высокий этаж
3	Вид на море
4	Тихий номер
5	Детская кроватка
6	Гипоаллергенное постельное
\.


--
-- Data for Name: guests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.guests (id, full_name, passport, phone, email, loyalty_tier, total_spend) FROM stdin;
2	Смирнова Ольга Викторовна	4501 654321	+7-900-222-3344	smirnova@mail.ru	Silver	12000.00
3	Козлов Дмитрий Петрович	4502 111222	+7-900-333-4455	kozlov@gmail.com	Platinum	120000.00
4	Новикова Екатерина Ивановна	4503 333444	+7-900-444-5566	novikova@yandex.ru	Silver	5000.00
5	Морозов Сергей Андреевич	4504 555666	+7-900-555-6677	morozov@mail.ru	Gold	55000.00
6	Васильева Наталья Сергеевна	4505 777888	+7-900-666-7788	vasileva@inbox.ru	Silver	8000.00
7	Павлов Михаил Юрьевич	4506 999000	+7-900-777-8899	pavlov@gmail.com	Platinum	200000.00
8	Захарова Анастасия Олеговна	4507 121314	+7-900-888-9900	zaharova@mail.ru	Silver	2000.00
9	Степанов Виктор Николаевич	4508 151617	+7-901-100-2000	stepanov@yandex.ru	Gold	38000.00
10	Федорова Мария Александровна	4509 181920	+7-901-200-3000	fedorova@gmail.com	Silver	15000.00
1	Иванов Алексей Николаевич	4500 123456	+7-900-111-2233	ivanov@mail.ru	Gold	64800.00
\.


--
-- Data for Name: hotels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hotels (id, name, address, director_name, overbooking_limit, latitude, longitude) FROM stdin;
1	Гранд Отель Центр	ул. Ленина, 1, Москва	Петров Иван Сергеевич	10	55.755825	37.617298
2	Бизнес Отель Аэропорт	Аэропортовое шоссе, 5, Москва	Сидорова Анна Петровна	15	55.972642	37.414981
3	Отель у Моря	Набережная, 12, Сочи	Козлов Дмитрий Андреевич	5	43.599237	39.725685
4	Гранд Отель Центр	ул. Ленина, 1, Москва	Петров Иван Сергеевич	10	\N	\N
5	Бизнес Отель Аэропорт	Аэропортовое шоссе, 5, Москва	Сидорова Анна Петровна	15	\N	\N
6	Отель у Моря	Набережная, 12, Сочи	Козлов Дмитрий Андреевич	5	\N	\N
\.


--
-- Data for Name: refund_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.refund_requests (id, booking_id, guest_id, amount, status, created_at, resolved_at, manager_id) FROM stdin;
\.


--
-- Data for Name: replenishment_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.replenishment_requests (id, staff_id, hotel_id, item_name, quantity, unit, status, created_at) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews (id, booking_id, guest_id, hotel_id, rating, comment, created_at) FROM stdin;
\.


--
-- Data for Name: room_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.room_categories (id, name, base_price, capacity) FROM stdin;
1	Standard	3500.00	2
2	Lux	7000.00	2
3	President	15000.00	4
4	Economy	2000.00	1
5	Standard	3500.00	2
6	Lux	7000.00	2
7	President	15000.00	4
8	Economy	2000.00	1
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rooms (id, hotel_id, category_id, room_number, cleaning_status, room_condition) FROM stdin;
2	1	1	102	Dirty	Исправно
3	1	2	201	Clean	Исправно
4	1	2	202	Cleaning	Исправно
6	1	4	1	Clean	Ремонт
7	2	1	110	Clean	Исправно
8	2	1	111	Clean	Исправно
9	2	2	210	Dirty	Исправно
10	2	3	310	Clean	Исправно
11	3	1	101	Clean	Исправно
12	3	2	201	Clean	Исправно
13	3	3	301	Clean	Исправно
1	1	1	101	Dirty	Исправно
5	1	3	301	Dirty	Исправно
\.


--
-- Data for Name: service_orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.service_orders (id, booking_id, service_id, quantity, ordered_at) FROM stdin;
1	1	1	4	2025-05-01 09:00:00
2	1	4	1	2025-05-02 14:00:00
3	2	1	2	2025-05-10 09:00:00
4	3	6	1	2025-06-01 10:00:00
5	3	1	7	2025-06-02 09:00:00
6	4	1	2	2025-06-15 09:00:00
7	5	5	1	2025-07-01 08:00:00
8	5	1	9	2025-07-01 09:00:00
9	7	4	2	2025-08-02 15:00:00
10	7	1	6	2025-08-01 09:00:00
11	1	1	4	2025-05-01 09:00:00
12	1	4	1	2025-05-02 14:00:00
13	2	1	2	2025-05-10 09:00:00
14	3	6	1	2025-06-01 10:00:00
15	3	1	7	2025-06-02 09:00:00
16	4	1	2	2025-06-15 09:00:00
17	5	5	1	2025-07-01 08:00:00
18	5	1	9	2025-07-01 09:00:00
19	7	4	2	2025-08-02 15:00:00
20	7	1	6	2025-08-01 09:00:00
\.


--
-- Data for Name: service_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.service_requests (id, admin_id, manager_id, hotel_id, description, status, created_at) FROM stdin;
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.services (id, name, price, is_package) FROM stdin;
1	Завтрак	500.00	f
2	Обед	800.00	f
3	Ужин	900.00	f
4	SPA	3000.00	f
5	Трансфер	2000.00	f
6	Пакет Романтик	8000.00	t
7	Пакет Семейный	6000.00	t
8	Уборка	300.00	f
9	Прачечная	200.00	f
10	Завтрак	500.00	f
11	Обед	800.00	f
12	Ужин	900.00	f
13	SPA	3000.00	f
14	Трансфер	2000.00	f
15	Пакет Романтик	8000.00	t
16	Пакет Семейный	6000.00	t
17	Уборка	300.00	f
18	Прачечная	200.00	f
\.


--
-- Data for Name: staff; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff (id, hotel_id, full_name, role, login, password_hash, manager_id) FROM stdin;
3	1	Борисов Павел Николаевич	Техник	tech1	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
1	1	Николаева Юлия Сергеевна	Менеджер	admin1	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
4	2	Орлова Ирина Петровна	Администратор	admin2	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
2	1	Громова Светлана Ивановна	Уборщик	cleaner1	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
5	2	Зайцева Алина Олеговна	Уборщик	cleaner2	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
7	3	Тихонова Валерия Андреевна	Уборщик	cleaner3	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
6	3	Лебедев Константин Юрьевич	Менеджер	admin3	$2b$12$hJXHwGxTINkYGEE2oVlPUepRgH2/igQZ2bW2LdRv0m99BT4FU6goe	\N
\.


--
-- Data for Name: staff_schedules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff_schedules (id, staff_id, work_date, shift, note) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, guest_id, login, password_hash, created_at) FROM stdin;
1	1	tourist1	$2b$12$BhNH8cwqDHQuRtatEkryxeV4/D23eEGZ7BLPMo7ltpheKCLCH5Sta	2026-05-26 16:59:33.101032
\.


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: bookings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bookings_id_seq', 26, true);


--
-- Name: guest_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.guest_preferences_id_seq', 12, true);


--
-- Name: guests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.guests_id_seq', 20, true);


--
-- Name: hotels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hotels_id_seq', 6, true);


--
-- Name: refund_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.refund_requests_id_seq', 1, false);


--
-- Name: replenishment_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.replenishment_requests_id_seq', 1, false);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reviews_id_seq', 1, false);


--
-- Name: room_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.room_categories_id_seq', 8, true);


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rooms_id_seq', 26, true);


--
-- Name: service_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.service_orders_id_seq', 20, true);


--
-- Name: service_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.service_requests_id_seq', 1, false);


--
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.services_id_seq', 18, true);


--
-- Name: staff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.staff_id_seq', 14, true);


--
-- Name: staff_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.staff_schedules_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: _migrations _migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public._migrations
    ADD CONSTRAINT _migrations_pkey PRIMARY KEY (filename);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: guest_pref_link guest_pref_link_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_pref_link
    ADD CONSTRAINT guest_pref_link_pkey PRIMARY KEY (guest_id, preference_id);


--
-- Name: guest_preferences guest_preferences_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_preferences
    ADD CONSTRAINT guest_preferences_name_key UNIQUE (name);


--
-- Name: guest_preferences guest_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_preferences
    ADD CONSTRAINT guest_preferences_pkey PRIMARY KEY (id);


--
-- Name: guests guests_passport_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guests
    ADD CONSTRAINT guests_passport_key UNIQUE (passport);


--
-- Name: guests guests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guests
    ADD CONSTRAINT guests_pkey PRIMARY KEY (id);


--
-- Name: hotels hotels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_pkey PRIMARY KEY (id);


--
-- Name: refund_requests refund_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refund_requests
    ADD CONSTRAINT refund_requests_pkey PRIMARY KEY (id);


--
-- Name: replenishment_requests replenishment_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.replenishment_requests
    ADD CONSTRAINT replenishment_requests_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_booking_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_booking_id_key UNIQUE (booking_id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: room_categories room_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room_categories
    ADD CONSTRAINT room_categories_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_hotel_id_room_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_hotel_id_room_number_key UNIQUE (hotel_id, room_number);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: service_orders service_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_orders
    ADD CONSTRAINT service_orders_pkey PRIMARY KEY (id);


--
-- Name: service_requests service_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: staff staff_login_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_login_key UNIQUE (login);


--
-- Name: staff staff_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (id);


--
-- Name: staff_schedules staff_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_pkey PRIMARY KEY (id);


--
-- Name: staff_schedules staff_schedules_staff_id_work_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_staff_id_work_date_key UNIQUE (staff_id, work_date);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_staff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_staff ON public.audit_log USING btree (staff_id);


--
-- Name: idx_audit_table; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_table ON public.audit_log USING btree (table_name);


--
-- Name: idx_bookings_dates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bookings_dates ON public.bookings USING btree (check_in, check_out);


--
-- Name: idx_bookings_guest; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bookings_guest ON public.bookings USING btree (guest_id);


--
-- Name: idx_bookings_room; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bookings_room ON public.bookings USING btree (room_id);


--
-- Name: idx_replenish_staff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_replenish_staff ON public.replenishment_requests USING btree (staff_id);


--
-- Name: idx_reviews_hotel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reviews_hotel ON public.reviews USING btree (hotel_id);


--
-- Name: idx_rooms_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rooms_category ON public.rooms USING btree (category_id);


--
-- Name: idx_rooms_hotel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rooms_hotel ON public.rooms USING btree (hotel_id);


--
-- Name: idx_schedules_staff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedules_staff ON public.staff_schedules USING btree (staff_id, work_date);


--
-- Name: idx_service_req_hotel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_service_req_hotel ON public.service_requests USING btree (hotel_id);


--
-- Name: audit_log audit_log_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
-- Name: bookings bookings_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES public.guests(id);


--
-- Name: bookings bookings_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- Name: bookings bookings_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
-- Name: guest_pref_link guest_pref_link_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_pref_link
    ADD CONSTRAINT guest_pref_link_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES public.guests(id) ON DELETE CASCADE;


--
-- Name: guest_pref_link guest_pref_link_preference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.guest_pref_link
    ADD CONSTRAINT guest_pref_link_preference_id_fkey FOREIGN KEY (preference_id) REFERENCES public.guest_preferences(id) ON DELETE CASCADE;


--
-- Name: refund_requests refund_requests_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refund_requests
    ADD CONSTRAINT refund_requests_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id);


--
-- Name: refund_requests refund_requests_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refund_requests
    ADD CONSTRAINT refund_requests_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES public.guests(id);


--
-- Name: refund_requests refund_requests_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refund_requests
    ADD CONSTRAINT refund_requests_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.staff(id);


--
-- Name: replenishment_requests replenishment_requests_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.replenishment_requests
    ADD CONSTRAINT replenishment_requests_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- Name: replenishment_requests replenishment_requests_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.replenishment_requests
    ADD CONSTRAINT replenishment_requests_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
-- Name: reviews reviews_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id);


--
-- Name: reviews reviews_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES public.guests(id);


--
-- Name: reviews reviews_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- Name: rooms rooms_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.room_categories(id);


--
-- Name: rooms rooms_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id) ON DELETE CASCADE;


--
-- Name: service_orders service_orders_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_orders
    ADD CONSTRAINT service_orders_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: service_orders service_orders_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_orders
    ADD CONSTRAINT service_orders_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- Name: service_requests service_requests_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.staff(id);


--
-- Name: service_requests service_requests_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- Name: service_requests service_requests_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.service_requests
    ADD CONSTRAINT service_requests_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.staff(id);


--
-- Name: staff staff_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id) ON DELETE CASCADE;


--
-- Name: staff staff_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.staff(id);


--
-- Name: staff_schedules staff_schedules_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_schedules
    ADD CONSTRAINT staff_schedules_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id) ON DELETE CASCADE;


--
-- Name: users users_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES public.guests(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict wxNR4eNRqMSkNKzBwnlNdlzUjzmh0u23Cuee8BnLvs5M6LhGkFed07d2Fq4EKgW

