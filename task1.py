import sys
import os

def init_author_dict():
    # maps AID to author name
    names = dict()
    for line in open('microsoft/Authors.txt'):
        data = line.rstrip().split('\t')
        AID = data[0]
        name = data[1]
        names[AID] = name
    return names
        
def init_paper_author_dict():
    # maps PID to list of authors that are a pair of (author_id, affiliation)
    d = dict()
    for line in open('microsoft/PaperAuthorAffiliations.txt'):
        data = line.rstrip().split('\t')
        PID = data[0]
        AID = data[1]
        aff = data[4]
        seq_num = data[5]
        author_obj = [AID, aff]
        if PID not in d:
            d[PID] = list()
        d[PID].append(author_obj)
    return d        

def init_paper_keywords_dict():
    # maps PID to set of keywords found in PaperKeywords.txt
    keywords = dict()
    for line in open('microsoft/PaperKeywords.txt'):
        data = line.rstrip().split('\t')
        PID = data[0]
        word = data[1]
        if PID not in keywords:
            keywords[PID] = set()
        keywords[PID].add(word)
    return keywords

def init_index_dict():
    # maps PID to (PDFID, folder)
    index = dict()
    for line in open('microsoft/index.txt'):
        data = line.rstrip().split('\t')
        folder = data[0]
        PDFID = data[1]
        PID = data[2]
        index[PID] = [PDFID, folder]
    return index

def concat_list(li):
    # given a list concatenate it into a string with | as seperators 
    str = ''
    for i, x in enumerate(li):
        if i < len(li)-1:
            str += x
            str += '|'
        else:
            str += x
    return str

class Paper(object):
    def __init__(self, pid, title, year, conf):
        self.PID = pid
        self.authors = set()
        self.author_ids = set()
        self.keywords = set()
        self.conf = conf
        self.year = year
        self.title = title
        try:
            self.PDFID = index_dict[self.PID][0]
            self.folder = index_dict[self.PID][1]
        except KeyError:
            self.PDFID = 'na'
            self.folder = 'na'
        self.affil = ''
        
    def make_author_sets(self):
        # paper_author maps PID to (author_id, affiliation)
        author_pairs = paper_author[self.PID]
        for pair in author_pairs:
            id = pair[0]
            self.author_ids.add(id)
        # author_names maps AID to author name
        for id in self.author_ids:
            name = author_names[id]
            self.authors.add(name)
    
    def set_affil(self, affil_dict):
        # uses paper_author dict PID:(AID, affil)
        author_affils = affil_dict[self.PID]
        self.affil = author_affils[0][1]
    
    def make_keyword_set(self):
        try:
            self.keywords = paper_keywords[self.PID]
        except KeyError:
            self.keywords.add('na')

if __name__ == '__main__':
    # csv for PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords
    integrated_data = open('data/integrated.csv', 'w+')
    # initialize the dictionaries 
    author_names = init_author_dict() # key: AID, value: Author name
    print('Number of authors: {}'.format(str(len(author_names))))
    paper_author = init_paper_author_dict() # key: PID, value: [AID, aff]
    paper_keywords = init_paper_keywords_dict()
    index_dict = init_index_dict()
    author_titles = dict() # stores the key as the author name and the value as all of their titles

    # CSV header
    integrated_data.write("PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords\n")
    num_papers = 0
    # process Papers
    for line in open('microsoft/Papers.txt'):
        data = line.rstrip().split('\t')
        # parse data
        PID = data[0]       
        title = data[2]
        year = int(data[3])
        conf = data[7]
        
        # error checking 
        confs = {'icdm', 'kdd', 'wsdm', 'www'}
        if conf not in confs:
            continue
        if year > 2016 or year < 1994:
            continue
            
        # make new Paper object
        paper = Paper(PID, title, year, conf)
        paper.make_author_sets()
        paper.set_affil(paper_author)
        temp_key = paper.make_keyword_set()
        
        if paper.PDFID == 'na':
            continue
        
        # output all the data 
        paper_data = "{},{},{},{},{},{},{},{},{},{}\n".format(paper.PID, 
                                                      paper.PDFID, 
                                                      paper.title, 
                                                      paper.conf,
                                                      paper.folder,
                                                      paper.year,
                                                      paper.affil,
                                                      concat_list(paper.authors),
                                                      concat_list(paper.author_ids),
                                                      concat_list(paper.keywords)
                                                    )
        integrated_data.write(paper_data)
        num_papers += 1
        
    print('Number of papers: {}'.format(str(num_papers)))