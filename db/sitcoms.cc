#include <cassert>
#include <cctype>
#include <cstring>
#include <set>
#include <fstream>
#include <set>
#include <sys/queue.h>
#include <string_view>
#include <cstdio>
#include <iostream>
#include <filesystem>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <optional>
#include <ranges>
#include <algorithm>
#include <print>
#include <generator>
#include <map>

#include <lowdown.h>

static std::string program_name;

struct Date
{
	std::chrono::year year;
	std::optional<std::chrono::month> month;
};

template<typename T>
struct inclusive_range
{
	T from, to;

	using value_type = T;
	using difference_type = std::ptrdiff_t;
	using iterator_category = std::forward_iterator_tag;

	constexpr inclusive_range begin() const { return *this; }
	constexpr inclusive_range end() const { auto end = to; return { .from = ++end, .to = to }; }

	T operator*() const { return from; }
	inclusive_range& operator++() { ++from; return *this; }
	inclusive_range operator++(int) { return { .from = from++, .to = to }; }

	bool operator==(inclusive_range<T> const&) const = default;
	auto operator<=>(inclusive_range<T> const&) const = default;

	bool contains(T const& rhs)
	{
		return from <= rhs && rhs <= to;
	}
};

static_assert(std::forward_iterator<inclusive_range<int>>);
static_assert(std::ranges::forward_range<inclusive_range<int>>);

using Seasons = std::vector<inclusive_range<std::chrono::year>>;
using Watched = std::map<std::size_t, Date>;
using Networks = std::vector<std::string>;

struct Series
{
	std::string path;
	std::string_view title;
	std::string_view review;
	Networks networks;

	Watched watched;
	Seasons seasons;
	std::vector<std::string> tags;
	std::size_t score;
	bool musical_episode = false;

	static Series from_file(char const* path);
	void dump();

	inclusive_range<std::chrono::year> bounds() const
	{
		assert(seasons.size());
		return {seasons.front().from, seasons.back().to};
	}

	auto operator<=>(Series const& other) const
	{
		assert(seasons.size());
		assert(other.seasons.size());

		if (auto cmp = bounds() <=> other.bounds(); cmp == 0) {
			return title <=> other.title;
		} else {
			return cmp;
		}
	}
};

Seasons parse_seasons_declaration(std::string_view s)
{
	std::size_t expected_number = 1;
	std::size_t number;
	enum {
		SEASON_NUMBER,
		YEAR_RANGE,
	} state = SEASON_NUMBER;

	Seasons seasons;

	while (s.size()) {
		while (s.size() && std::isspace(s.front())) s.remove_prefix(1);
		if (s.empty()) break;

		auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
		assert(ec == std::errc{}); // TODO: Implement better error handling
		s = { p, s.data() + s.size() };

		switch (state) {
		break; case SEASON_NUMBER: {
			assert(expected_number == number); // TODO: error handling
			++expected_number;
			state = YEAR_RANGE;
		}
		break; case YEAR_RANGE: {
			auto &year = seasons.emplace_back();
			year.from = std::chrono::year(number);
			if (s.starts_with("..")) {
				s.remove_prefix(2);
				auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
				assert(ec == std::errc{}); // TODO: Implement better error handling
				s = { p, s.data() + s.size() };
				year.to = std::chrono::year(number);
			} else {
				year.to = year.from;
			}
			state = SEASON_NUMBER;
		}
		}
	}

	assert(state == SEASON_NUMBER);

	return seasons;
}

Watched parse_watched_declaration(std::string_view s) {
	std::size_t number;
	enum {
		SEASON_RANGE,
		YEAR_MONTH,
	} state = SEASON_RANGE;

	Watched watched;

	inclusive_range<std::size_t> season_range;

	while (s.size()) {
		while (s.size() && std::isspace(s.front())) s.remove_prefix(1);
		if (s.empty()) break;

		auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
		assert(ec == std::errc{}); // TODO: Implement better error handling
		s = { p, s.data() + s.size() };

		switch (state) {
		break; case SEASON_RANGE: {
			season_range.from = season_range.to = number;
			if (s.starts_with("..")) {
				s.remove_prefix(2);
				auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
				assert(ec == std::errc{}); // TODO: Implement better error handling
				s = { p, s.data() + s.size() };
				season_range.to = number;
			}
			state = YEAR_MONTH;
		}
		break; case YEAR_MONTH: {
			Date date;
			date.year = std::chrono::year(number);

			if (s.starts_with("-")) {
				s.remove_prefix(1);
				auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), number);
				assert(ec == std::errc{}); // TODO: Implement better error handling
				s = { p, s.data() + s.size() };
				date.month = std::chrono::month(number);
			}

			for (auto season : season_range) {
				watched[season] = date;
			}

			state = SEASON_RANGE;
		}
		}
	}

	assert(state == SEASON_RANGE);

	return watched;
}

std::string_view trim(std::string_view s)
{
	while (s.size() && isspace(s.front())) s.remove_prefix(1);
	while (s.size() && isspace(s.back())) s.remove_suffix(1);
	return s;
}

Networks parse_networks_declaration(std::string_view s)
{
	Networks networks;

	while (s.size()) {
		auto const split = s.find(',');
		if (split == std::string_view::npos) {
			networks.emplace_back(trim(s));
			s = {};
		} else {
			networks.emplace_back(trim(s.substr(0, split)));
			s.remove_prefix(split + 1);
		}
	}

	return networks;
}

Series Series::from_file(char const* path)
{
	Series series;
	series.path = path;

	struct lowdown_opts opts = {};
	opts.type = LOWDOWN_HTML;
	opts.feat = LOWDOWN_COMMONMARK
		        | LOWDOWN_FENCED
						| LOWDOWN_AUTOLINK
						| LOWDOWN_METADATA;
	opts.oflags = LOWDOWN_HTML_HEAD_IDS;

	struct lowdown_metaq mq = {}; // Don't deallocate since it's field are later used
	struct lowdown_meta *m;
	TAILQ_INIT(&mq);

	char *ret = NULL; // Don't deallocate since it's used later to store review
	size_t retsz = 0;

	std::unique_ptr<FILE, int(*)(FILE*)> source(fopen(path, "r"), fclose);

	if (!lowdown_file(&opts, source.get(), &ret, &retsz, &mq)) {
		std::cerr << program_name << ": error: failed to render markdown for " << path << "\n";
		exit(1);
	}

	TAILQ_FOREACH(m, &mq, entries) {
		std::string_view key = m->key;
		if (0) {}
		else if (key == "title")   { series.title   = m->value; }
		else if (key == "tags") {
			std::string next;
			for (std::istringstream ss{m->value}; ss >> next;) {
				series.tags.push_back(next);
			}
		}
		else if (key == "watched") { series.watched = parse_watched_declaration(m->value); }
		else if (key == "seasons") { series.seasons = parse_seasons_declaration(m->value); }
		else if (key == "network") { series.networks = parse_networks_declaration(m->value); }
		else if (key == "musical-episode") { series.musical_episode = true; }
		else if (key == "score") {
			auto [p, ec] = std::from_chars(m->value, m->value + std::strlen(m->value), series.score);
			assert(ec == std::errc{});
		}
		else {
			std::cerr << program_name << ": error: " << path << ": unrecognized metadata key: " << m->key << "\n";
			continue;
		}
	}

	series.review = { ret, retsz };

	return series;
}

void Series::dump()
{
	auto [min, max] = std::ranges::minmax(std::views::join(seasons));
	std::cout << title << " (" << min << "-" << max << "):";
	for (auto const& t : tags) std::cout << " #" << t;
	std::cout << '\n';
}

struct Series_Collection
{
	std::vector<std::shared_ptr<Series>> series;
	std::unordered_multimap<std::string, std::shared_ptr<Series>> tags;

	static Series_Collection from_directory(std::filesystem::path root);
};

Series_Collection Series_Collection::from_directory(std::filesystem::path root)
{
	Series_Collection s;

	for (auto d : std::filesystem::directory_iterator{root}) {
		auto p = d.path();
		s.series.emplace_back(new Series(Series::from_file(p.c_str())));
		auto &series = s.series.back();
		for (auto const& tag : series->tags) {
			s.tags.insert(std::pair{tag, series});
		}
	}

	return s;
}

std::string pretty_print_watched(Series const& series)
{
	size_t last_season_watched = 0;
	std::chrono::year finished_watching_in;

	for (auto [season_number, date] : series.watched) {
		last_season_watched = std::max(last_season_watched, season_number);
		finished_watching_in = date.year;
	}

	if (last_season_watched == series.seasons.size()) {
		return std::format("finished in {}", finished_watching_in);
	} else {
		return std::format("stopped at season {} in {}", last_season_watched, finished_watching_in);
	}
}

int main(int, char **argv)
{
	program_name = std::filesystem::path(argv[0]).filename().string();

	auto coll = Series_Collection::from_directory("./series/");

	std::ofstream sitcoms_output_file{"sitcoms.html", std::ios::trunc|std::ios::out};

	auto out = [&sitcoms_output_file](auto &&value) {
		sitcoms_output_file << value;
	};

	auto [sitcom_begin, sitcom_end] = coll.tags.equal_range("sitcom");
	auto sitcoms = std::ranges::subrange(sitcom_begin, sitcom_end)
			| std::views::transform([](auto &p) -> auto& { return p.second; })
			| std::ranges::to<std::vector>();
	std::ranges::sort(sitcoms, std::less<>{}, [](auto const& x) -> auto const& { return *x; });

	auto const [year_start, year_end] = std::ranges::minmax(
			sitcoms
		| std::views::transform([](auto const& s) { return s->seasons; })
		| std::views::join
		| std::views::join);


	std::map<std::chrono::year, std::size_t> sitcoms_in_each_year;
	for (auto year : sitcoms
			| std::views::transform([](auto const& s) { return s->bounds(); })
			| std::views::join
	) {
		++sitcoms_in_each_year[year];
	}
	auto years_with_sitcom_count = std::move(sitcoms_in_each_year) | std::ranges::to<std::vector>();
	assert(std::ranges::is_sorted(years_with_sitcom_count));
	auto year_with_most_sitcoms = std::ranges::max_element(years_with_sitcom_count, [](auto const& l, auto const& r) { return l.second < r.second; });


	auto years_with_most_sitcoms_range = std::ranges::subrange{year_with_most_sitcoms, years_with_sitcom_count.end()}
			| std::views::take_while([&](auto const& p) { return p.second == year_with_most_sitcoms->second; })
			| std::views::enumerate;

	std::string years_with_most_sitcoms;
	{
		auto count = std::ranges::distance(std::ranges::begin(years_with_most_sitcoms_range), std::ranges::end(years_with_most_sitcoms_range));
		for (auto [i, x] : years_with_most_sitcoms_range) {
			if (i != 0) {
				if (i+1 == count) {
					years_with_most_sitcoms += " and ";
				} else {
					years_with_most_sitcoms += ", ";
				}
			}
			years_with_most_sitcoms += std::format("{}", x.first);
		}
	}
	auto const years_count = (year_end - year_start).count();

	std::map<std::chrono::year, std::size_t> seasons_watched_in_year;
	std::map<std::chrono::year, std::size_t> sitcoms_watched_in_year;

	for (auto const& sitcom : sitcoms) {
		auto const years = sitcom->watched | std::views::values | std::views::transform(&Date::year);
		for (auto year : years | std::ranges::to<std::set>()) {
			sitcoms_watched_in_year[year]++;
		}
		for (auto year : years) {
			seasons_watched_in_year[year]++;
		}
	}

	auto shows_with_musical_episodes = sitcoms
		| std::views::filter([](auto const& s) { return s->musical_episode; })
		| std::views::transform([](auto const& s) { return s->title; })
		| std::ranges::to<std::vector>();

	auto shows_with_musical_episodes_list = std::string{};

	for (auto [i, x] : std::views::enumerate(shows_with_musical_episodes)) {
			if (i != 0) {
				if (i+1 == std::ranges::ssize(shows_with_musical_episodes)) {
					shows_with_musical_episodes_list += " and ";
				} else {
					shows_with_musical_episodes_list += ", ";
				}
			}
			shows_with_musical_episodes_list += x;
		}

	std::map<std::string, std::set<std::string>> networks;

	for (auto const& show : sitcoms) {
		for (auto network : show->networks) {
			networks[network].insert(std::string(show->title));
		}
	}


#include "sitcoms.hh"

	return 0;
}
