#include <array>
#include <cassert>
#include <concepts>
#include <filesystem>
#include <fstream>
#include <print>
#include <string_view>
#include <utility>
#include <vector>

struct Comma_Separated_List
{
	std::string_view value;

	struct iterator
	{
		std::string_view value;

		std::string_view operator*() const
		{
			auto n = value.find(',');
			return n == std::string_view::npos ? value : value.substr(0, n);
		}

		iterator& operator++()
		{

		}
	};

	iterator begin() { return iterator{value}; }
	iterator end() { return {}; }
};

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
	std::string_view genres; // TODO: Make an array

	auto as_tuple()
	{
		return std::tie(
			tconst, title_type, primary_title, original_title, is_adult,
			start_year, end_year, runtime_minutes, genres
		);
	}
};

struct Movie
{
	std::string_view title;
	unsigned year;
	std::optional<Title_Basics> imdb_info = {};
};

constinit auto MOVIES = std::array {
	Movie { .title = "A View to a Kill", .year = 1985 },
	Movie { .title = "After Hours", .year = 1985 },
	Movie { .title = "Avengers: Age of Ultron", .year = 2015 },
	Movie { .title = "Back to the Future", .year = 1985 },
	Movie { .title = "Bad Boys", .year = 1995 },
	Movie { .title = "Batman Begins", .year = 2005 },
	Movie { .title = "Batman Forever", .year = 1995 },
	Movie { .title = "Charlie and the Chocolate Factory", .year = 2005 },
	Movie { .title = "Chicken Little", .year = 2005 },
	Movie { .title = "Constantine", .year = 2005 },
	Movie { .title = "Creed", .year = 2015 },
	Movie { .title = "Day of the Dead", .year = 1985 },
	Movie { .title = "Death Race 2000", .year = 1975 },
	Movie { .title = "Dog Day Afternoon", .year = 1975 },
	Movie { .title = "Elektra", .year = 2005 },
	Movie { .title = "Fantastic Four", .year = 2005 },
	Movie { .title = "Fantastic Four", .year = 2015 },
	Movie { .title = "Furious 7", .year = 2015 },
	Movie { .title = "Ghost in the Shell", .year = 1995 },
	Movie { .title = "GoldenEye", .year = 1995 },
	Movie { .title = "Hackers", .year = 1995 },
	Movie { .title = "Inside Out", .year = 2015 },
	Movie { .title = "Jaws", .year = 1975 },
	Movie { .title = "Johnny Mnemonic", .year = 1995 },
	Movie { .title = "Judge Dredd", .year = 1995 },
	Movie { .title = "Jumanji", .year = 1995 },
	Movie { .title = "King Kong", .year = 2005 },
	Movie { .title = "Kiss Kiss Bang Bang", .year = 2005 },
	Movie { .title = "Lassie", .year = 2005 },
	Movie { .title = "Mad Max: Fury Road", .year = 2015 },
	Movie { .title = "Madagascar", .year = 2005 },
	Movie { .title = "The Martian", .year = 2015 },
	Movie { .title = "Mission: Impossible - Rogue Nation", .year = 2015 },
	Movie { .title = "Monty Python and the Holy Grail", .year = 1975 },
	Movie { .title = "Mortal Kombat", .year = 1995 },
	Movie { .title = "Mr. & Mrs. Smith", .year = 2005 },
	Movie { .title = "Pitch Perfect 2", .year = 2015 },
	Movie { .title = "Pride & Prejudice", .year = 2005 },
	Movie { .title = "Re-Animator", .year = 1985 },
	Movie { .title = "Robots", .year = 2005 },
	Movie { .title = "Shaun the Sheep Movie", .year = 2015 },
	Movie { .title = "Sicario", .year = 2015 },
	Movie { .title = "Sin City", .year = 2005 },
	Movie { .title = "Spectre", .year = 2015 },
	Movie { .title = "Spotlight", .year = 2015 },
	Movie { .title = "Star Wars: Episode VII - The Force Awakens", .year = 2015 },
	Movie { .title = "Terror of Mechagodzilla", .year = 1975 },
	Movie { .title = "The Big Short", .year = 2015 },
	Movie { .title = "The Breakfast Club", .year = 1985 },
	Movie { .title = "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe", .year = 2005 },
	Movie { .title = "The Goonies", .year = 1985 },
	Movie { .title = "The Hateful Eight", .year = 2015 },
	Movie { .title = "The Man from U.N.C.L.E.", .year = 2015 },
	Movie { .title = "The Return of the Living Dead", .year = 1985 },
	Movie { .title = "The Rocky Horror Picture Show", .year = 1975 },
	Movie { .title = "The Sound of Music", .year = 1965 },
	Movie { .title = "The Transporter Refueled", .year = 2015 },
	Movie { .title = "The Witch", .year = 2015 },
	Movie { .title = "The World's Fastest Indian", .year = 2005 },
	Movie { .title = "Thunderball", .year = 1965 },
	Movie { .title = "Corpse Bride", .year = 2005 },
	Movie { .title = "Toy Story", .year = 1995 },
	Movie { .title = "Transporter 2", .year = 2005 },
	Movie { .title = "Wallace & Gromit: The Curse of the Were-Rabbit", .year = 2005 },
	Movie { .title = "War of the Worlds", .year = 2005 },
	Movie { .title = "xXx: State of the Union", .year = 2005 },
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
	auto data = tsv::from_file<Title_Basics>("title.basics.tsv", true);

	for (Title_Basics const& entry : data) {
		for (Movie& movie : MOVIES) {
			if (entry.title_type == "movie" && (entry.primary_title == movie.title || entry.original_title == movie.title) && entry.start_year == movie.year) {
				movie.imdb_info = entry;
			}
		}
	}

	for (auto const& movie : MOVIES) {
		std::print("{}: {}\n", movie.title, movie.imdb_info->genres);
		assert(movie.imdb_info != std::nullopt);
	}

	return 0;
}
