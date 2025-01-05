function SearchBar() {
  return (
      <div className="search-container mgr2" id="searchBar">
        <input
          type="text"
          className="form-control search-input"
          placeholder="Search..."
        />
        <i className="fas fa-search search-icon"></i>
      </div>
  );
}

export default SearchBar;
