// The words and numbers shown on the home page and in the syllabus list.
// AQRJ staff can change this file without touching any page code.
//
// Everything marked DRAF is a placeholder for AQRJ to confirm or replace.
// Text here is in Bahasa Melayu because the public pages are BM only.

/** What a learner needs to open a level. Each plan includes the ones before it. */
export type PlanId = 'percuma' | 'asas' | 'penuh';

export const PLAN_ORDER: readonly PlanId[] = ['percuma', 'asas', 'penuh'];

export type Plan = {
	id: PlanId;
	name: string;
	/** Ringgit a month. 0 means free. */
	priceRm: number;
	summary: string;
	features: string[];
	highlight?: boolean;
};

export const PLANS: readonly Plan[] = [
	{
		id: 'percuma',
		name: 'Percuma',
		priceRm: 0,
		summary: 'Cuba dahulu. Tiada kad, tiada bayaran.',
		features: ['Tahap 1 dan 2', 'Video pelajaran pendek', 'Kuiz dan jejak kemajuan']
	},
	{
		id: 'asas',
		name: 'Asas',
		priceRm: 29,
		summary: 'Separuh pertama silibus: daripada kenal huruf hingga lancar Iqra’.',
		features: ['Tahap 1 hingga 4', 'Semua dalam pelan Percuma', 'Semakan bacaan oleh ustazah']
	},
	{
		id: 'penuh',
		name: 'Penuh',
		priceRm: 49,
		summary: 'Silibus penuh: Iqra’, tajwid, tilawah dan hafazan.',
		features: ['Semua 8 tahap', 'Semua dalam pelan Asas', 'Kelas talaqqi langsung dan sijil'],
		highlight: true
	}
];

export type SyllabusLevel = {
	number: number;
	title: string;
	summary: string;
	/** The lowest plan that opens this level. */
	plan: PlanId;
	lessons: string[];
};

// DRAF: silibus contoh. Tahap 1 hingga 4 ialah separuh pertama (pelan Asas).
export const SYLLABUS: readonly SyllabusLevel[] = [
	{
		number: 1,
		title: 'Kenal huruf hijaiyah',
		summary: 'Mengenal dan menyebut 28 huruf dengan makhraj yang betul.',
		plan: 'percuma',
		lessons: ['Huruf alif hingga kha', 'Huruf dal hingga dhad', 'Huruf tha hingga ya', 'Ulang kaji']
	},
	{
		number: 2,
		title: 'Baris dan sambung huruf',
		summary: 'Baris atas, bawah dan depan, serta huruf bersambung (Iqra’ 1 dan 2).',
		plan: 'percuma',
		lessons: ['Baris fathah', 'Baris kasrah dan dhammah', 'Huruf bersambung', 'Latihan bacaan']
	},
	{
		number: 3,
		title: 'Mad dan tanwin',
		summary: 'Bacaan panjang, tanwin dan sukun (Iqra’ 3 dan 4).',
		plan: 'asas',
		lessons: ['Mad asli', 'Tanwin', 'Sukun dan qalqalah', 'Latihan bacaan']
	},
	{
		number: 4,
		title: 'Lancar Iqra’',
		summary: 'Sabdu, waqaf dan bacaan ayat penuh (Iqra’ 5 dan 6).',
		plan: 'asas',
		lessons: ['Tasydid', 'Alif lam', 'Tanda waqaf', 'Ujian tamat Iqra’']
	},
	{
		number: 5,
		title: 'Tilawah Juz Amma',
		summary: 'Membaca surah-surah pendek dengan lancar.',
		plan: 'penuh',
		lessons: ['An-Nas hingga Ad-Dhuha', 'Al-Lail hingga Al-A’la', 'At-Tariq hingga An-Naba’']
	},
	{
		number: 6,
		title: 'Tajwid lengkap',
		summary: 'Hukum nun mati, mim mati, mad dan sifat huruf.',
		plan: 'penuh',
		lessons: ['Nun mati dan tanwin', 'Mim mati', 'Jenis-jenis mad', 'Makhraj dan sifat huruf']
	},
	{
		number: 7,
		title: 'Tilawah Al-Quran',
		summary: 'Membaca 30 juzuk dengan bimbingan dan semakan berkala.',
		plan: 'penuh',
		lessons: ['Juzuk 1 hingga 10', 'Juzuk 11 hingga 20', 'Juzuk 21 hingga 30']
	},
	{
		number: 8,
		title: 'Hafazan surah pilihan',
		summary: 'Menghafaz surah lazim dengan kaedah ulangan.',
		plan: 'penuh',
		lessons: ['Kaedah menghafaz', 'Surah lazim', 'Yasin, Al-Mulk dan As-Sajdah']
	}
];

// DRAF: gantikan dengan butiran sebenar ustazah sebelum pelancaran.
// Letak gambar di static/images/ dan isi `photo`, contohnya '/images/ustazah.webp'.
export const TEACHER = {
	name: 'Ustazah AQRJ',
	role: 'Pengasas dan guru utama, Akademi Quran Raudhatul Jannah',
	photo: null as string | null,
	intro:
		'Profil ustazah akan dikemas kini di sini: latar belakang pengajian, pengalaman mengajar dan pendekatan beliau di dalam kelas.',
	points: [
		'Kelas untuk semua peringkat umur, daripada kanak-kanak hingga dewasa',
		'Pelajar muslimat disemak oleh ustazah',
		'Belajar ikut kadar sendiri, dengan bimbingan guru'
	]
};

/** True when `owned` opens a level that needs `needed`. */
export function planIncludes(owned: PlanId, needed: PlanId): boolean {
	return PLAN_ORDER.indexOf(owned) >= PLAN_ORDER.indexOf(needed);
}
