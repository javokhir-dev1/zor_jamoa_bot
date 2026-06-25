--
-- PostgreSQL database dump
--

\restrict vabUrHLOdSf8CKrCKwla8Y7E3d2a3fRDXU5cTkalM3NTkeumaQ6zgdVKeuHtwSJ

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

--
-- Name: mealtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mealtype AS ENUM (
    'tushlik',
    'kechki_ovqat'
);


ALTER TYPE public.mealtype OWNER TO postgres;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'employee',
    'dept_head',
    'admin'
);


ALTER TYPE public.userrole OWNER TO postgres;

--
-- Name: userstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userstatus AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.userstatus OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    head_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departments_id_seq OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    ordered_by_user_id integer NOT NULL,
    order_date date NOT NULL,
    meal_type public.mealtype NOT NULL,
    is_taken boolean DEFAULT false NOT NULL,
    taken_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    full_name character varying(200) NOT NULL,
    phone_number character varying(20),
    department_id integer,
    role public.userrole DEFAULT 'employee'::public.userrole NOT NULL,
    status public.userstatus DEFAULT 'pending'::public.userstatus NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
0001
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (id, name, head_user_id, created_at) FROM stdin;
1	BUKUN	\N	2026-06-18 20:53:31.243969+00
2	Tasvirchilar	\N	2026-06-18 20:59:35.458695+00
3	Montajchilar	\N	2026-06-18 20:59:40.440685+00
4	Chiroqchilar	\N	2026-06-18 20:59:50.576276+00
5	Ovoz rejissyorlari	\N	2026-06-18 21:00:00.03598+00
6	Monitorchilar	\N	2026-06-18 21:00:12.456021+00
8	Efirka	\N	2026-06-18 21:00:25.318984+00
7	IT Bo'limi	\N	2026-06-18 21:00:21.036087+00
9	Zo'rplay	\N	2026-06-18 21:00:44.150429+00
10	Ma'muriyat	\N	2026-06-18 21:01:01.852309+00
11	KPP - POST	\N	2026-06-18 21:01:13.749673+00
12	Bojalar pr	\N	2026-06-18 21:01:24.21438+00
13	M Xo'ja pr	\N	2026-06-18 21:01:37.250134+00
14	Ovoz pr	\N	2026-06-18 21:01:44.476587+00
15	ART Dizayn	\N	2026-06-18 21:01:52.795156+00
16	Texnik bo'lim	\N	2026-06-18 21:02:21.289513+00
17	Ustalar	\N	2026-06-18 21:03:28.898774+00
18	A Baxtiyorovich pr	\N	2026-06-18 21:04:01.17802+00
19	Haydovchilar	\N	2026-06-18 21:04:48.715613+00
20	Dublyaj	\N	2026-06-19 04:06:04.526404+00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, user_id, ordered_by_user_id, order_date, meal_type, is_taken, taken_at, created_at) FROM stdin;
1	3	3	2026-06-20	tushlik	f	\N	2026-06-18 20:58:36.359736+00
2	3	3	2026-06-20	kechki_ovqat	f	\N	2026-06-18 20:58:44.024637+00
3	7	7	2026-06-20	tushlik	f	\N	2026-06-19 03:09:57.661421+00
4	17	17	2026-06-20	tushlik	f	\N	2026-06-19 03:21:58.004242+00
5	15	15	2026-06-20	tushlik	f	\N	2026-06-19 03:24:07.957485+00
6	12	12	2026-06-20	tushlik	f	\N	2026-06-19 03:25:49.632692+00
7	12	12	2026-06-20	kechki_ovqat	f	\N	2026-06-19 03:26:00.389932+00
8	11	11	2026-06-20	tushlik	f	\N	2026-06-19 03:41:53.984246+00
9	11	11	2026-06-20	kechki_ovqat	f	\N	2026-06-19 03:41:56.013387+00
10	14	14	2026-06-20	tushlik	f	\N	2026-06-19 03:44:39.887012+00
11	6	6	2026-06-20	tushlik	f	\N	2026-06-19 03:54:39.982363+00
12	18	18	2026-06-20	tushlik	f	\N	2026-06-19 03:56:42.388656+00
13	20	20	2026-06-20	tushlik	f	\N	2026-06-19 03:57:19.365031+00
14	13	13	2026-06-20	tushlik	f	\N	2026-06-19 04:01:11.251559+00
15	25	25	2026-06-20	tushlik	f	\N	2026-06-19 04:05:12.639409+00
16	19	19	2026-06-20	tushlik	f	\N	2026-06-19 04:07:05.495397+00
17	19	19	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:07:07.160171+00
18	21	21	2026-06-20	tushlik	f	\N	2026-06-19 04:10:09.668783+00
19	29	29	2026-06-20	tushlik	f	\N	2026-06-19 04:27:45.216255+00
20	31	31	2026-06-20	tushlik	f	\N	2026-06-19 04:27:45.913341+00
21	33	33	2026-06-20	tushlik	f	\N	2026-06-19 04:27:56.327197+00
22	33	33	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:28:01.686103+00
23	31	31	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:28:05.661575+00
24	34	34	2026-06-20	tushlik	f	\N	2026-06-19 04:28:26.114671+00
25	27	27	2026-06-20	tushlik	f	\N	2026-06-19 04:28:41.298301+00
26	9	9	2026-06-20	tushlik	f	\N	2026-06-19 04:31:57.394181+00
27	9	9	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:32:31.61745+00
28	26	26	2026-06-20	tushlik	f	\N	2026-06-19 04:33:38.663147+00
29	39	39	2026-06-20	tushlik	f	\N	2026-06-19 04:38:05.129375+00
30	39	39	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:38:07.665394+00
31	42	42	2026-06-20	tushlik	f	\N	2026-06-19 04:42:16.179171+00
32	44	44	2026-06-20	tushlik	f	\N	2026-06-19 04:42:21.797032+00
33	46	46	2026-06-20	tushlik	f	\N	2026-06-19 04:49:42.027762+00
34	46	46	2026-06-20	kechki_ovqat	f	\N	2026-06-19 04:49:43.625344+00
35	47	47	2026-06-20	tushlik	f	\N	2026-06-19 04:52:30.753416+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, telegram_id, full_name, phone_number, department_id, role, status, created_at, updated_at) FROM stdin;
1	7761304842	Javohir	\N	\N	admin	approved	2026-06-18 20:53:23.854877+00	2026-06-18 20:53:23.89784+00
31	7597422615	Olimxon otaxonov	+998944516600	4	employee	approved	2026-06-19 04:24:35.290336+00	2026-06-19 04:27:29.999288+00
32	743005497	Qurbonova Mahliyo Akramovna	+998935561990	16	employee	approved	2026-06-19 04:24:57.863532+00	2026-06-19 04:27:33.124844+00
3	5552033632	Muslimbek Abdurahimov	+998996874111	1	admin	approved	2026-06-18 20:58:14.116933+00	2026-06-18 20:58:26.273514+00
4	1399897720	Toshkentov Baxtishod	+998983317366	8	employee	approved	2026-06-18 21:05:42.425736+00	2026-06-18 21:06:02.504632+00
2	716572736	Farrux	+998974430226	1	admin	approved	2026-06-18 20:54:23.905161+00	2026-06-18 21:06:58.042073+00
5	717784738	Hasanov Shaxzodbek	+998902816668	5	employee	approved	2026-06-18 21:24:17.072285+00	2026-06-19 02:23:14.712991+00
6	1214649364	Sarvar Sharofiddinov	+998907812323	5	employee	approved	2026-06-18 23:10:05.498016+00	2026-06-19 02:23:19.325018+00
7	5007992717	Ashurov Doston.	+998911045050	6	employee	approved	2026-06-18 23:52:16.522843+00	2026-06-19 02:23:20.872651+00
8	95186977	Ulug'bek Ilhomov	+998998110131	2	employee	approved	2026-06-19 01:53:01.525409+00	2026-06-19 02:23:22.933752+00
9	119098181	Юсупова Феруза	+998903577706	10	employee	approved	2026-06-19 01:55:40.235643+00	2026-06-19 02:23:25.792862+00
10	823771462	Арифова Нафиса	+998909797580	16	employee	approved	2026-06-19 02:11:09.126596+00	2026-06-19 02:23:35.072133+00
11	5796858076	Abilxairov Abduqodir	+998952223038	16	employee	approved	2026-06-19 02:28:45.64566+00	2026-06-19 03:20:27.82846+00
12	5438132365	Abdusamatov Isroil	+998881113360	19	employee	approved	2026-06-19 02:32:02.05591+00	2026-06-19 03:20:29.661285+00
33	7399039496	Imomqulova Sevinch	+998507882848	1	employee	approved	2026-06-19 04:25:45.498345+00	2026-06-19 04:27:34.980243+00
14	6275021368	Qobulov shohruh shovkat ogli	+998935071740	19	employee	approved	2026-06-19 02:47:52.421471+00	2026-06-19 03:20:32.512478+00
15	1027029095	Sardor Qurbonaliyev	+998977224344	3	employee	approved	2026-06-19 03:17:14.574726+00	2026-06-19 03:20:33.960022+00
16	923528353	Xamroyev Barkamol	+998974130083	2	employee	approved	2026-06-19 03:19:00.63641+00	2026-06-19 03:20:35.176412+00
17	554556411	Baxtiyor Jalilov	+998998656883	2	employee	approved	2026-06-19 03:20:22.57633+00	2026-06-19 03:20:42.206946+00
18	8006253456	Boynazarov Diyorbek	+998500374949	4	employee	approved	2026-06-19 03:33:31.035788+00	2026-06-19 03:56:10.882474+00
19	5392356850	Zokirov Begzo	+998971457475	1	employee	approved	2026-06-19 03:54:16.918436+00	2026-06-19 03:56:14.290382+00
21	6180870441	Ixtiyor Orziqulov	+998949441030	1	employee	approved	2026-06-19 03:57:11.120881+00	2026-06-19 03:59:18.81186+00
22	5185830065	Билялова Аида	+998940072773	8	employee	approved	2026-06-19 03:57:34.193026+00	2026-06-19 03:59:20.332462+00
23	5789847678	Ruxshona Xabibullayeva Dinmuxammad qizi	+998937821181	1	employee	approved	2026-06-19 03:58:46.388722+00	2026-06-19 03:59:24.675775+00
24	5586179914	Diyora Soatova	+998880092373	1	employee	approved	2026-06-19 03:59:22.40642+00	2026-06-19 03:59:27.014951+00
25	682495463	Guzal Shodiyeva	+998995585403	1	employee	approved	2026-06-19 04:03:49.290794+00	2026-06-19 04:04:09.529614+00
13	6783429305	Firdavs Dublyaj	+998970071525	20	employee	approved	2026-06-19 02:42:01.996422+00	2026-06-19 04:07:30.669612+00
20	7490699058	Zilola Abdinabiyeva	+998991404369	20	employee	approved	2026-06-19 03:56:35.65967+00	2026-06-19 04:08:31.550599+00
26	5654509944	Туронбека Шарофиддинова	+998973306436	10	employee	approved	2026-06-19 04:11:30.9916+00	2026-06-19 04:27:19.548497+00
27	628561183	Атаджонов Жамшид	+998997207587	2	employee	approved	2026-06-19 04:12:52.19774+00	2026-06-19 04:27:21.254548+00
28	8549779031	Iskandarov Otabek	+998909421441	20	employee	approved	2026-06-19 04:13:27.076947+00	2026-06-19 04:27:23.114005+00
29	24499476	Dilyara Meldebekova	+998977033836	18	employee	approved	2026-06-19 04:14:11.055087+00	2026-06-19 04:27:25.051577+00
30	1248053299	Деканбаева Мукаддам	+998998917300	16	employee	approved	2026-06-19 04:19:30.931747+00	2026-06-19 04:27:27.116276+00
34	6624933740	Oybek Karimov	+998999811777	10	employee	approved	2026-06-19 04:27:35.985537+00	2026-06-19 04:27:41.592243+00
40	786643614	Билялов Махмуд	+998946952773	8	employee	approved	2026-06-19 04:36:54.04463+00	2026-06-19 04:37:09.551276+00
35	1124864212	Sardor Abdurahmonov	+998900072112	18	employee	approved	2026-06-19 04:30:24.332677+00	2026-06-19 04:37:16.299787+00
36	6972994341	Abdulhamid Hasanov	+12284446263	1	employee	approved	2026-06-19 04:30:48.32373+00	2026-06-19 04:37:16.985315+00
37	940349683	Jasmina Jamolova	+998887173837	1	employee	approved	2026-06-19 04:32:12.891951+00	2026-06-19 04:37:17.76924+00
38	1239226522	Furkat Saidmamatov	+998935785710	2	employee	approved	2026-06-19 04:33:37.159914+00	2026-06-19 04:37:19.908309+00
39	5302430783	Asaloy	+998996894111	1	employee	approved	2026-06-19 04:36:40.692686+00	2026-06-19 04:37:21.533479+00
41	5739366570	Gulnoza Hojiyeva	+998500072800	1	employee	approved	2026-06-19 04:36:57.429798+00	2026-06-19 04:37:22.667886+00
42	7475011816	Mardonova Sevinch Ikrom qizi	+998970270750	1	employee	approved	2026-06-19 04:37:46.111944+00	2026-06-19 04:41:37.907527+00
43	831090968	Yadgarova Nilufar Marifjanovna	+998903309622	16	employee	approved	2026-06-19 04:38:40.953334+00	2026-06-19 04:41:49.147635+00
44	335635553	Xolbo'tayev Baxtiyor	+998994044471	11	employee	approved	2026-06-19 04:41:01.210921+00	2026-06-19 04:41:52.967345+00
45	6507966263	Shahzod Abdullayev	+998940772614	1	employee	approved	2026-06-19 04:42:33.135713+00	2026-06-19 04:44:14.840129+00
46	5996441536	Mohichexra Yusufjonova	+998917541710	1	employee	approved	2026-06-19 04:48:05.923815+00	2026-06-19 04:48:49.389665+00
47	5951613590	Saloxiddin Faxriddinov	+998941931577	5	employee	approved	2026-06-19 04:50:33.739565+00	2026-06-19 04:52:16.515793+00
48	408913762	Эргешов Атабек Адашбекович	+998998546596	19	employee	approved	2026-06-19 04:52:21.489792+00	2026-06-19 04:56:32.962202+00
49	60357279	Позилжонов Шовозбек	+998905266601	10	employee	approved	2026-06-19 04:56:09.380039+00	2026-06-19 04:56:33.935297+00
\.


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departments_id_seq', 20, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 35, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 49, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: orders uq_user_date_meal; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT uq_user_date_meal UNIQUE (user_id, order_date, meal_type);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: ix_orders_order_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_order_date ON public.orders USING btree (order_date);


--
-- Name: ix_orders_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_user_id ON public.orders USING btree (user_id);


--
-- Name: ix_users_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: departments fk_dept_head; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_user_id) REFERENCES public.users(id);


--
-- Name: orders orders_ordered_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_ordered_by_user_id_fkey FOREIGN KEY (ordered_by_user_id) REFERENCES public.users(id);


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- PostgreSQL database dump complete
--

\unrestrict vabUrHLOdSf8CKrCKwla8Y7E3d2a3fRDXU5cTkalM3NTkeumaQ6zgdVKeuHtwSJ

