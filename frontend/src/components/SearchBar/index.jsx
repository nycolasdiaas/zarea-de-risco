function SearchBar(){
    return (
        <div className="col-md-4 d-flex align-self-end">
        <div className="search-container align-self-end m-3 mgr2" id="">
          <input
            type="text"
            className="form-control search-input"
            placeholder="Search..."
          />
          <i className="fas fa-search search-icon"></i>
        </div>
      </div>
    );
}

export default SearchBar;
