#include <algorithm>
#include <array>
#include <set>
#include <cassert>
#include <concepts>
#include <filesystem>
#include <fstream>
#include <map>
#include <print>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

// Sources for movies:
// ...
// https://editorial.rottentomatoes.com/guide/best-movies-1995/
// https://editorial.rottentomatoes.com/guide/best-movies-2005/
// ...

struct Comma_Separated_List
{
	std::string_view value;

	struct iterator
	{
		using difference_type = std::ptrdiff_t;
		using value_type = std::string_view;

		std::string_view value;

		value_type operator*() const
		{
			auto n = value.find(',');
			return n == std::string_view::npos ? value : value.substr(0, n);
		}

		iterator& operator++()
		{
			auto n = value.find(',');
			if (n == std::string_view::npos) {
				value = {};
			} else {
				value.remove_prefix(n+1);
			}
			return *this;
		}

		iterator operator++(int)
		{
			auto copy = *this;
			++*this;
			return copy;
		}

		bool operator==(iterator const& other) const
		{
			return value == other.value;
		}
	};

	iterator begin() const { return iterator{value}; }
	iterator end() const { return {}; }
};

template<>
struct std::formatter<Comma_Separated_List> : std::formatter<std::string_view>
{
	auto format(Comma_Separated_List const& arg, std::format_context& ctx) const
	{
		std::string temp;
		temp += '[';

		for (auto it = arg.begin(); it != arg.end();) {
			temp += *it;
			temp += ++it == arg.end() ? ']' : ',';
		}

		return std::formatter<std::string_view>::format(temp, ctx);
	}
};

static_assert(std::forward_iterator<typename Comma_Separated_List::iterator>);
static_assert(std::ranges::forward_range<Comma_Separated_List>);

struct Title_Basics
{
	std::string_view tconst;
	std::string_view title_type; // TODO: Make an enum
	std::string_view primary_title;
	std::string_view original_title;
	bool is_adult;
	unsigned start_year;
	unsigned end_year;
	unsigned runtime_minutes;
	Comma_Separated_List genres; // TODO: Make an array

	auto as_tuple()
	{
		return std::tie(
			tconst, title_type, primary_title, original_title, is_adult,
			start_year, end_year, runtime_minutes, genres
		);
	}
};

enum class Tag : unsigned long long
{
	None = 0,

	Bond = 1 << 0,
	Transporter = 1 << 1,
	Comic_Book = 1 << 2,
	Jason_Statham = 1 << 3,
	Mad_Max = 1 << 4,
	Tom_Cruise = 1 << 5,
	Tim_Burton = 1 << 6,
	Guy_Ritchie = 1 << 7,
	Keanu_Reeves = 1 << 8,
};

constexpr Tag operator|(Tag lhs, Tag rhs)
{
	return Tag(std::to_underlying(lhs) | std::to_underlying(rhs));
}

std::ostream& operator<<(std::ostream& os, Tag tag)
{
	switch (tag) {
	case Tag::Bond: return os << "James Bond";
	case Tag::Transporter: return os << "Transporter";
	case Tag::Comic_Book: return os << "Comic Book Adaptations";
	case Tag::Jason_Statham: return os << "Jason Statham";
	case Tag::Mad_Max: return os << "Mad Max";
	case Tag::Tom_Cruise: return os << "Tom Cruise";
	case Tag::Tim_Burton: return os << "Tim Burton";
	case Tag::Guy_Ritchie: return os << "Guy Ritchie";
	case Tag::Keanu_Reeves: return os << "Keanu Reeves";


	case Tag::None:;
	}

	assert(0 && "unreachable");
}

template<typename T>
struct Bit_Iterator
{
	using value_type = Tag;
	using difference_type = std::ptrdiff_t;

	Tag value;

	value_type operator*() const
	{
		return Tag(std::bit_floor(std::to_underlying(value)));
	}

	Bit_Iterator& operator++()
	{
		auto bits = std::to_underlying(value);
		value = Tag(~std::bit_floor(bits) & bits);
		return *this;
	}

	Bit_Iterator operator++(int)
	{
		auto copy = *this;
		++*this;
		return copy;
	}

	bool operator==(Bit_Iterator const&) const = default;
};

Bit_Iterator<Tag> begin(Tag value)
{
	return { .value = value };
}

Bit_Iterator<Tag> end(Tag)
{
	return { .value = Tag::None };
}

static_assert(std::input_iterator<Bit_Iterator<Tag>>);
static_assert(std::ranges::input_range<Tag>);

struct Movie
{
	std::string_view title;
	unsigned year;
	std::optional<Title_Basics> imdb_info = {};
	std::optional<int> score = std::nullopt;
	Tag tag = Tag::None;
};

constinit auto MOVIES = std::array {
	Movie { .title = "12 Monkeys", .year = 1995 },
	Movie { .title = "A View to a Kill", .year = 1985, .tag = Tag::Bond },
	Movie { .title = "A Walk in the Clouds", .year = 1995, .tag = Tag::Keanu_Reeves },
	Movie { .title = "A Working Man", .year = 2025, .score = 2, .tag = Tag::Jason_Statham },
	Movie { .title = "After Hours", .year = 1985 },
	Movie { .title = "Ant-Man", .year = 2015, .score = 4, .tag = Tag::Comic_Book },
	Movie { .title = "Avengers: Age of Ultron", .year = 2015, .score = 5, .tag = Tag::Comic_Book },
	Movie { .title = "Back to the Future", .year = 1985, .score = 9 },
	Movie { .title = "Bad Boys", .year = 1995 },
	Movie { .title = "Ballerina", .year = 2025, .tag = Tag::Keanu_Reeves },
	Movie { .title = "Batman Begins", .year = 2005, .score = 7, .tag = Tag::Comic_Book },
	Movie { .title = "Batman Forever", .year = 1995, .tag = Tag::Comic_Book | Tag::Tim_Burton },
	Movie { .title = "Black Bag", .year = 2025 },
	Movie { .title = "Captain America: Brave New World", .year = 2025, .score = 4, .tag = Tag::Comic_Book },
	Movie { .title = "Chaos", .year = 2015, .tag = Tag::Jason_Statham },
	Movie { .title = "Charlie and the Chocolate Factory", .year = 2005, .score = 2 },
	Movie { .title = "Chicken Little", .year = 2005 },
	Movie { .title = "Cinderella", .year = 2015 },
	Movie { .title = "Constantine", .year = 2005, .score = 9, .tag = Tag::Comic_Book | Tag::Keanu_Reeves },
	Movie { .title = "Corpse Bride", .year = 2005, .tag = Tag::Tim_Burton },
	Movie { .title = "Creed", .year = 2015 },
	Movie { .title = "Day of the Dead", .year = 1985 },
	Movie { .title = "Death Race 2000", .year = 1975 },
	Movie { .title = "Descendants", .year = 2015, .score = 7 },
	Movie { .title = "Desperado", .year = 1995 },
	Movie { .title = "Dog Day Afternoon", .year = 1975 },
	Movie { .title = "Elektra", .year = 2005, .tag = Tag::Comic_Book },
	Movie { .title = "Fantastic Four", .year = 2005, .tag = Tag::Comic_Book },
	Movie { .title = "Fantastic Four", .year = 2015, .tag = Tag::Comic_Book },
	Movie { .title = "Fountain of Youth", .year = 2025, .tag = Tag::Guy_Ritchie },
	Movie { .title = "Furious 7", .year = 2015, .score = 10 },
	Movie { .title = "Ghost in the Shell", .year = 1995 },
	Movie { .title = "GoldenEye", .year = 1995, .tag = Tag::Bond },
	Movie { .title = "Hackers", .year = 1995 },
	Movie { .title = "How to Train Your Dragon", .year = 2025, .score = 7 },
	Movie { .title = "Inside Out", .year = 2015, .score = 8 },
	Movie { .title = "Jaws", .year = 1975 },
	Movie { .title = "Johnny Mnemonic", .year = 1995, .tag = Tag::Keanu_Reeves },
	Movie { .title = "Judge Dredd", .year = 1995, .tag = Tag::Comic_Book },
	Movie { .title = "Jumanji", .year = 1995 },
	Movie { .title = "King Kong", .year = 2005 },
	Movie { .title = "Kiss Kiss Bang Bang", .year = 2005 },
	Movie { .title = "Knock Knock", .year = 2015, .tag = Tag::Keanu_Reeves },
	Movie { .title = "La haine", .year = 1995 },
	Movie { .title = "Lassie", .year = 2005 },
	Movie { .title = "Legend", .year = 1985, .tag = Tag::Tom_Cruise },
	Movie { .title = "London", .year = 2005, .tag = Tag::Jason_Statham },
	Movie { .title = "Mad Max Beyond Thunderdome", .year = 1985, .tag = Tag::Mad_Max },
	Movie { .title = "Mad Max: Fury Road", .year = 2015, .score = 10, .tag = Tag::Mad_Max },
	Movie { .title = "Madagascar", .year = 2005 },
	Movie { .title = "Mickey 17", .year = 2025 },
	Movie { .title = "Mission: Impossible - Rogue Nation", .year = 2015, .tag = Tag::Tom_Cruise },
	Movie { .title = "Mission: Impossible - The Final Reckoning", .year = 2025, .score = 3, .tag = Tag::Tom_Cruise },
	Movie { .title = "Monty Python and the Holy Grail", .year = 1975, .score = 8 },
	Movie { .title = "Mortal Kombat", .year = 1995 },
	Movie { .title = "Mr. & Mrs. Smith", .year = 2005 },
	Movie { .title = "Pitch Perfect 2", .year = 2015, .score = 6 },
	Movie { .title = "Pocahontas", .year = 1995 },
	Movie { .title = "Pride & Prejudice", .year = 2005 },
	Movie { .title = "Rambo: First Blood Part II", .year = 1985, .score = 5 },
	Movie { .title = "Re-Animator", .year = 1985 },
	Movie { .title = "Revolver", .year = 2005, .tag = Tag::Jason_Statham | Tag::Guy_Ritchie },
	Movie { .title = "Robots", .year = 2005 },
	Movie { .title = "Shaun the Sheep Movie", .year = 2015 },
	Movie { .title = "Sicario", .year = 2015 },
	Movie { .title = "Sin City", .year = 2005, .tag = Tag::Comic_Book },
	Movie { .title = "Sinners", .year = 2025, .score = 10 },
	Movie { .title = "Snow White", .year = 2025, .score = 5 },
	Movie { .title = "Spectre", .year = 2015, .tag = Tag::Bond },
	Movie { .title = "Spotlight", .year = 2015 },
	Movie { .title = "Spy", .year = 2015 },
	Movie { .title = "Star Wars: Episode VII - The Force Awakens", .year = 2015, .score = 5 },
	Movie { .title = "Terminator Genisys", .year = 2015, .score = 2 },
	Movie { .title = "Terror of Mechagodzilla", .year = 1975 },
	Movie { .title = "The Amateur", .year = 2025 },
	Movie { .title = "The Big Short", .year = 2015 },
	Movie { .title = "The Breakfast Club", .year = 1985, .score = 10 },
	Movie { .title = "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe", .year = 2005 },
	Movie { .title = "The Goonies", .year = 1985 },
	Movie { .title = "The Hateful Eight", .year = 2015 },
	Movie { .title = "The Incredibly True Adventure of Two Girls in Love", .year = 1995 },
	Movie { .title = "The Man from U.N.C.L.E.", .year = 2015, .score = 9, .tag = Tag::Guy_Ritchie },
	Movie { .title = "The Martian", .year = 2015 },
	Movie { .title = "The Monkey", .year = 2025 },
	Movie { .title = "The Phoenician Scheme", .year = 2025, .score = 8 },
	Movie { .title = "The Return of the Living Dead", .year = 1985 },
	Movie { .title = "The Rocky Horror Picture Show", .year = 1975 },
	Movie { .title = "The Sound of Music", .year = 1965 },
	Movie { .title = "The Transporter Refueled", .year = 2015, .score = 5, .tag = Tag::Transporter },
	Movie { .title = "The Witch", .year = 2015 },
	Movie { .title = "The World's Fastest Indian", .year = 2005 },
	Movie { .title = "Thunderball", .year = 1965, .tag = Tag::Bond },
	Movie { .title = "Thunderbolts*", .year = 2025, .score = 8, .tag = Tag::Comic_Book },
	Movie { .title = "Toy Story", .year = 1995 },
	Movie { .title = "Transporter 2", .year = 2005, .score = 7, .tag = Tag::Transporter },
	Movie { .title = "Wallace & Gromit: The Curse of the Were-Rabbit", .year = 2005 },
	Movie { .title = "War of the Worlds", .year = 2005, .tag = Tag::Tom_Cruise },
	Movie { .title = "Wild Card", .year = 2015, .tag = Tag::Jason_Statham },
	Movie { .title = "xXx: State of the Union", .year = 2005, .score = 10 },
	Movie { .title = "Æon Flux", .year = 2005 },
};

namespace tsv
{
	namespace details
	{
		inline std::string_view yield_cell(std::string_view &source)
		{
			auto next_start = source.find('\t');

			if (next_start == std::string_view::npos) {
				return std::exchange(source, std::string_view{});
			}

			auto ret = source.substr(0, next_start);
			source.remove_prefix(next_start+1);
			return ret;
		}
	}

	inline void parse(std::integral auto &target, std::string_view source)
	{
		if (source == "\\N") {
			target = -1;
			return;
		}

		auto [p, ec] = std::from_chars(source.data(), source.data() + source.size(), target);
		if (ec != std::errc{}) {
			std::print(stderr, "error: couldn't parse integer: '{}'\n", source);
			std::exit(1);
		}

		assert(p == source.data() + source.size());
	}

	inline void parse(bool &target, std::string_view source)
	{
		target = source == "1";
	}

	inline void parse(std::string_view &target, std::string_view source)
	{
		target = source;
	}

	inline void parse(Comma_Separated_List &target, std::string_view source)
	{
		target.value = source;
	}

	template<typename Entry>
	std::vector<Entry> from_file(auto const& filename, bool skip_header = false)
	{
		auto fsize = std::filesystem::file_size(filename);

		// Note that we leak memory on purpose here: then we can only operate on std::string_views and not std::strings
		// leading to major performance gain
		auto data = new char[fsize];
		std::ifstream{filename}.read(data, fsize);
	auto source = std::string_view(data, fsize);

		std::vector<Entry> result;

		while (source.size()) {
			std::string_view line = source.substr(0, source.find('\n'));
			source.remove_prefix(line.size()+1);

			if (skip_header) {
				skip_header = false;
				continue;
			}
			std::apply([s = line](auto& ...refs) mutable { (parse(refs, details::yield_cell(s)), ...); }, result.emplace_back().as_tuple());
		}

		return result;
	}
}

int main()
{
	auto const data = tsv::from_file<Title_Basics>("title.basics.tsv", true);

	for (Title_Basics const& entry : data) {
		for (Movie& movie : MOVIES) {
			if ((entry.title_type == "movie" || entry.title_type == "tvMovie") && (entry.primary_title == movie.title || entry.original_title == movie.title) && entry.start_year == movie.year) {
				movie.imdb_info = entry;
			}
		}
	}

	auto const with_score_count = std::ranges::count_if(MOVIES, [](Movie m) { return m.score.has_value(); });
	auto const completed = with_score_count / (double)MOVIES.size() * 100.0;

	using MovieSet = std::set<Movie, decltype([](Movie const& a, Movie const& b) {
		if (auto cmp = b.score <=> a.score; cmp == 0) {
			return std::tie(a.year, a.title) < std::tie(b.year, b.title);
		} else {
			return cmp < 0;
		}
	})>;

	std::unordered_map<std::string_view, std::vector<Movie>> genres;
	std::unordered_map<unsigned, unsigned> scores;
	std::map<unsigned, MovieSet> by_year;
	std::unordered_map<Tag, MovieSet> by_tag;

	for (auto const& movie : MOVIES) {
		if (movie.imdb_info == std::nullopt) {
			std::println("Movie {} without IMDB info", movie.title);
			return 2;
		}

		by_year[movie.year].insert(movie);

		if (movie.score.has_value()) {
			++scores[*movie.score];
		}

		for (auto tag : movie.tag) {
			by_tag[tag].insert(movie);
		}

		for (auto genre : movie.imdb_info->genres) {
			genres[genre].push_back(movie);
		}
	}


	std::print("{:.2f}% of {} movies = {} movies\n", completed, MOVIES.size(), with_score_count);

	for (unsigned score = 1; score <= 10; ++score) {
		std::print("{:2}: {:2} ", score, scores[score]);
		for (int i = scores[score]; i > 0; --i) {
			std::print("+");
		}
		std::println();
	}

	for (auto const& [year, movies] : by_year) {
		auto const with_score_count = std::ranges::count_if(movies, [](Movie m) { return m.score.has_value(); });
		auto const completed = with_score_count / (double)movies.size() * 100.0;

		std::println("{} - {:.2f}% of {} movies = {} movies", year, completed, movies.size(), with_score_count);
		for (auto movie : movies) {
			if (movie.score) {
				std::println("  {:2} {}", *movie.score, movie.title);
			} else {
				std::println("     {}", movie.title);
			}
		}
	}

	std::ofstream decades_output_file{"decades.html", std::ios::trunc|std::ios::out};
	auto const out = [&decades_output_file](auto &&value) {
		decades_output_file << value;
	};

	#include "decades.hh"

	return 0;
}
